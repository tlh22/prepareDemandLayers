# -*- coding: utf-8 -*-
"""
/***************************************************************************
 prepareDemandLayers
                                 A QGIS plugin
 test4
                              -------------------
        begin                : 2016-02-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by TH
        email                : th@mhtc.co.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
"""from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources"""


#from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog
from qgis.PyQt.QtSql import QSqlDatabase
from qgis.PyQt.QtCore import (
    QObject,
    QTimer,
    pyqtSignal,
    QSettings, QTranslator, qVersion, QCoreApplication
)

from qgis.core import (
    QgsExpressionContextUtils,
    QgsExpression,
    QgsFeatureRequest,
    QgsMessageLog, QgsFeature, QgsGeometry,
    QgsTransaction, QgsTransactionGroup,
    QgsProject,
    QgsVectorFileWriter,
    QgsApplication,
    QgsVectorLayer,
    QgsFields, QgsDataSourceUri, QgsWkbTypes,
    QgsMapLayer, QgsCoordinateTransformContext
)

from qgis.gui import QgsFileWidget, QgsMapLayerComboBox
from qgis import processing

# Initialize Qt resources from file resources.py
#from .resources import *
import sys, traceback

# Import the code for the dialog
from prepareDemandLayers.prepareDemandLayers_dialog import prepareDemandLayersDialog
import os.path

class prepareDemandLayers:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        """locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Test4_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)"""

        # Create the dialog (after translation) and keep reference
        self.dlg = prepareDemandLayersDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&prepareDemandLayers')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'prepareDemandLayers')
        self.toolbar.setObjectName(u'prepareDemandLayers')

        self.dlg.lineEditDB.clear()
        self.dlg.pushButtonDB.clicked.connect(self.select_sqliteDB)

        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_dir)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('prepareDemandLayers', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/prepareDemandLayers/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'prepareDemandLayers'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&prepareDemandLayers'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_dir(self):
        #self.dlg.setFileMode(QtGui.QFileDialog.Directory)
        #self.dlg.setOption(QtGui.QFileDialog.ShowDirsOnly)
        dirname = QFileDialog.getExistingDirectory(self.dlg, "Select output directory ","", QFileDialog.ShowDirsOnly)
        self.dlg.lineEdit.setText(dirname)

    def select_sqliteDB(self):
        # self.dlg.setFileMode(QtGui.QFileDialog.Directory)
        # self.dlg.setOption(QtGui.QFileDialog.ShowDirsOnly)
        dBname = QFileDialog.getSaveFileName(self.dlg, "Select file ","", '*.gpkg')
        if dBname[0]:
            self.dlg.lineEditDB.setText(dBname[0])

        
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        createShapeFiles = False
        createGeoPackage = False
        self.dlg.show()

        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                self.dlg.layerSurveys.addItem( layer.name(), layer ) 
                self.dlg.layerSupply.addItem( layer.name(), layer ) 
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass
            indexSurveys = self.dlg.layerSurveys.currentIndex()
            layerSurveys = self.dlg.layerSurveys.itemData(indexSurveys)
            indexSupply = self.dlg.layerSupply.currentIndex()
            layerSupply = self.dlg.layerSupply.itemData(indexSupply)

            QMessageBox.information(self.iface.mainWindow(),"hello world","%s has %d features. Using %s" %(layerSurveys.name(),layerSurveys.featureCount(), layerSupply.name()))
            crs = layerSupply.crs()

            # Set up indexes
            idxSurveyID = layerSurveys.fields().indexFromName('SurveyID')
            idxSurveyTime = layerSurveys.fields().indexFromName('SurveyTimePeriod')
            idxSurveyDay = layerSurveys.fields().indexFromName('SurveyDay')

            idxSupplySurveyID = layerSupply.fields().indexFromName('SurveyID')
            idxSupplySurveyDay = layerSupply.fields().indexFromName('SurveyDay')
            idxSupplySurveyTime = layerSupply.fields().indexFromName('SurveyTime')

            idxSupplyGeometry = layerSupply.fields().indexFromName('geom')

            dirname = self.dlg.lineEdit.text()
            dBname = self.dlg.lineEditDB.text()

            if len(dirname)>0:
                QgsMessageLog.logMessage("Shape file choosen ..." + str(dirname), tag="TOMs panel")
                createShapeFiles = True

            if len(dBname)>0:
                QgsMessageLog.logMessage("Geopackage choosen ..." + str(dBname), tag="TOMs panel")
                # set up database links, etc
                """uri = QgsDataSourceUri()
                uri.setDatabase(dBname)
                schema = ''
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName(uri.database())
                db.open()
                #conn = db.connect(dBname)

                QgsMessageLog.logMessage("Spatialite choosen:" + str(dBname) + ":" + str(layerSupply.name()),
                                     tag="TOMs panel")

                attr = layerSupply.fields().toList()"""
                createGeoPackage = True

            featureSet = layerSurveys.getFeatures()
            idx = layerSurveys.fields().indexFromName('SurveyID')

            for feature in sorted(featureSet, key=lambda f: f[idx], reverse=True):
                #for feature in layerSurveys.getFeatures():

                surveyID = feature.attributes()[idxSurveyID]
                surveyTime = feature.attributes()[idxSurveyTime]
                surveyDay = feature.attributes()[idxSurveyDay]
                #QMessageBox.information(self.iface.mainWindow(),"Survey ID","%s at %s." %(surveyID,surveyTime))

                feats = [feat for feat in layerSupply.getFeatures()]

                # Now create a new layer of DemandInformation
                #layerName = "Demand_%s_%s_%s" %(surveyID, surveyDay, surveyTime)
                layerName = 'Demand_{id:02d}_{day}_{time}'.format(id=int(surveyID), day=surveyDay, time=surveyTime)

                QgsMessageLog.logMessage("Demand layer ..." + str(layerName), tag="TOMs panel")

                filePath = dirname + "\\" + layerName

                #QMessageBox.information(self.iface.mainWindow(),"UIname: ","%s" %(UIname))

                newDemandLayer, newDemandLayerName = self.prepareNewDemandLayer(layerSupply, surveyID, surveyDay, surveyTime)
                # Create shape file

                if createShapeFiles:

                    QgsMessageLog.logMessage("Shape file choosen ...", tag="TOMs panel")

                    filePath = dirname + "\\" + newDemandLayerName

                    save_options = QgsVectorFileWriter.SaveVectorOptions()
                    save_options.driverName = "ESRI Shapefile"
                    save_options.fileEncoding = "UTF-8"
                    transform_context = QgsProject.instance().transformContext()
                    error = QgsVectorFileWriter.writeAsVectorFormatV2(layer,
                                                                      filePath,
                                                                      transform_context,
                                                                      save_options)
                    if error[0] == QgsVectorFileWriter.NoError:
                        print("success again!")
                    else:
                        print(error)

                    vlayer = QgsVectorLayer(filePath + ".shp", newDemandLayerName, "ogr")
                    QgsProject.instance().instance().addMapLayer(vlayer)

                    if not vlayer.startEditing():
                        QgsMessageLog.logMessage(
                            "Error starting edit session on {} ...".format(filePath), tag="TOMs panel")
                        return False
                    demandFeatures = [feat for feat in newDemandLayer.getFeatures()]
                    check = vlayer.addFeatures(demandFeatures)

                    """for feat in newDemandLayer.getFeatures():
                        if not vlayer.changeAttributeValue(feat.id(), idxSupplySurveyID, surveyID):
                            QgsMessageLog.logMessage("Error changing field idxSupplySurveyID {}...".format(idxSupplySurveyID), tag="TOMs panel")
                            break
                        if not vlayer.changeAttributeValue(feat.id(), idxSupplySurveyDay, surveyDay):
                            QgsMessageLog.logMessage("Error changing field idxSupplySurveyDay {}...".format(idxSupplySurveyDay), tag="TOMs panel")
                            break
                        if not vlayer.changeAttributeValue(feat.id(), idxSupplySurveyTime, surveyTime):
                            QgsMessageLog.logMessage("Error changing field idxSupplySurveyTime {}...".format(idxSupplySurveyTime), tag="TOMs panel")
                            break"""

                    vlayer.commitChanges()

                elif createGeoPackage:
                    #writer = QgsVectorFileWriter.writeAsVectorFormat(layerSupply,filePath,"utf-8",None,"ESRI Shapefile")
                    #vlayer = QgsVectorLayer(filePath + ".shp", layerName, "ogr")

                    QgsMessageLog.logMessage("geoPackage choosen ..." + str(dBname) + ":" + str(layerName), tag="TOMs panel")

                    self.saveLayerToGeopackage(newDemandLayer, newDemandLayerName, dBname)
                    newLayerA = QgsVectorLayer(dBname + "|layername=" + newDemandLayerName, newDemandLayerName,
                                               "ogr")

                    newLayerA.reload()
                    newLayerA.updateFields()
                    newLayerA.updateExtents()

                    QgsProject.instance().addMapLayer(newLayerA)


                else:
                    QMessageBox.information(self.iface.mainWindow(), "hello world",
                                            "No format choosen")
                    return

                # Add .ui file

                #vlayer.setEditForm(UIname) # This is not working ... need to think how to do this
                #vlayer.setUiForm(UIname)

                #  Code for QGIS v3.0
                #editFormConfig = vlayer.editFormConfig()
                #editFormConfig.setUiForm(UIname)
                #vlayer.setEditFormConfig(editFormConfig)

                # Add style file

                #vlayer.loadNamedStyle(StyleName)
                
                #QMessageBox.information(self.iface.mainWindow(),"Layer added: " )
                """
                if not vlayer.isValid():
                    print "Layer failed to load!"
                #if QgsVectorFileWriter.NoError:
                #    QMessageBox.information(self.iface.mainWindow(),"Everything is fine")
                #    raise IOError('Can\'t create the file: {0}\n'.format(layer_path))

                vlayer.startEditing()
                for feat in vlayer.getFeatures():
                    vlayer.changeAttributeValue(feat.id(), idxSupplySurveyID, surveyID)
                    vlayer.changeAttributeValue(feat.id(), idxSupplySurveyDay, surveyDay)
                    vlayer.changeAttributeValue(feat.id(), idxSupplySurveyTime, surveyTime)

                vlayer.commitChanges()"""
                
                # update SurveyID and Time in Supply table

    def prepareNewDemandLayer(self, supplyLayer, surveyID, surveyDay, surveyTime):

        newDemandLayerName = 'Demand_{id:02d}_{day}_{time}'.format(id=int(surveyID), day=surveyDay, time=surveyTime)
        QgsMessageLog.logMessage("prepareNewDemandLayer: creating " + str(newDemandLayerName), tag="TOMs panel")

        #currCrs = supplyLayer.crs().toWkt()
        #currGeomType = supplyLayer.wkbType()

        # https://gis.stackexchange.com/questions/129513/accessing-processing-with-python
        # https://gis.stackexchange.com/questions/205947/duplicating-layer-in-memory-using-pyqgis

        supplyLayer.selectAll()
        newDemandLayer = processing.run("native:saveselectedfeatures", {'INPUT': supplyLayer, 'OUTPUT': 'memory:'})['OUTPUT']

        QgsMessageLog.logMessage("prepareNewDemandLayer: nr supply features: " + str(supplyLayer.featureCount()), tag="TOMs panel")

        idxSupplySurveyID = supplyLayer.fields().indexFromName('SurveyID')
        idxSupplySurveyDay = supplyLayer.fields().indexFromName('SurveyDay')
        idxSupplySurveyTime = supplyLayer.fields().indexFromName('SurveyTime')

        newDemandLayer.startEditing()

        for feature in newDemandLayer.getFeatures():

            newDemandLayer.changeAttributeValue(feature.id(), idxSupplySurveyID, surveyID)
            newDemandLayer.changeAttributeValue(feature.id(), idxSupplySurveyDay, surveyDay)
            newDemandLayer.changeAttributeValue(feature.id(), idxSupplySurveyTime, surveyTime)

        newDemandLayer.commitChanges()

        QgsMessageLog.logMessage("prepareNewDemandLayer: nr demand features: " + str(newDemandLayer.featureCount()), tag="TOMs panel")

        return newDemandLayer, newDemandLayerName

    def saveLayerToGeopackage(self, newLayer, newLayerName, fileName):

        #for newLayerName, newLayer in outputLayersList:
        write_result = False

        QgsMessageLog.logMessage("In saveLayerToGeopackage - {}, count:{}".format(newLayerName, newLayer.featureCount()), tag="TOMs panel")
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.layerName = newLayerName
        options.driverName = "GPKG"
        #options.sourceCRS = newLayer.crs()
        options.destCRS = newLayer.crs()
        #options.editionCapabilities = QgsVectorFileWriter.CanAddNewLayer

        geometry_column = 'geom'
        newURI = newLayer.dataProvider().uri()
        newURI.setDatabase(fileName)
        newURI.setDataSource('', newLayerName, geometry_column)
        newURI.setSrid = newLayer.crs()
        newURI.setTable = newLayer.name()
        #newURI.setKeyColumn = newLayer.primaryKeyAttributes()[0]
        options.datasourceOptions = [newURI.uri()]

        # check to see if file exists
        if os.path.isfile(fileName):
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        """ This approach is depreciated. 
            New approach is to use .create() function to create writer and then addFeatures(). 
            However, I can't quite make it work. There is something with addfeatures that doesn't work ... 
            see - https://gis.stackexchange.com/questions/353687/pyqgis-qgsvectorfilewriter-create-doesnt-flush-even-after-deleted
            """
        write_result, error_message = QgsVectorFileWriter.writeAsVectorFormatV2(
            newLayer,
            fileName,
            QgsCoordinateTransformContext(),
            options)

        if write_result != QgsVectorFileWriter.NoError:
            QgsMessageLog.logMessage("Error: {errorNr} on {layer}: {txt}".format(errorNr=write_result, layer=newLayerName, txt=error_message), tag="TOMs panel")
            #print(currLayer.name(), self.writer)

        return write_result
