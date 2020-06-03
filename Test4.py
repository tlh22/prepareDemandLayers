# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Test4
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Test4_dialog import Test4Dialog
import os.path
from PyQt4.QtSql import QSqlDatabase
import sys, traceback

class Test4:
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
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Test4_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = Test4Dialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Test4')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Test4')
        self.toolbar.setObjectName(u'Test4')

        self.dlg.lineEditDB.clear()
        self.dlg.pushButtonDB.clicked.connect(self.select_sqliteDB)

        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_dir)

        self.dlg.lineEditUI.clear()
        self.dlg.pushButtonUI.clicked.connect(self.select_UI_file)

        self.dlg.lineEditStyle.clear()
        self.dlg.pushButtonStyle.clicked.connect(self.select_Style_file)

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
        return QCoreApplication.translate('Test4', message)


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

        icon_path = ':/plugins/Test4/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Test4'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Test4'),
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
        dBname = QFileDialog.getOpenFileName(self.dlg, "Select file ","", '*.sqlite;*.gpkg')
        self.dlg.lineEditDB.setText(dBname)

    def select_UI_file(self):
        #self.dlg.setFileMode(QtGui.QFileDialog.Directory)
        #self.dlg.setOption(QtGui.QFileDialog.ShowDirsOnly)
        filename = QFileDialog.getOpenFileName(self.dlg, "Select file ","", '*.ui')
        self.dlg.lineEditUI.setText(filename)
        
    def select_Style_file(self):
        #self.dlg.setFileMode(QtGui.QFileDialog.Directory)
        #self.dlg.setOption(QtGui.QFileDialog.ShowDirsOnly)
        filename = QFileDialog.getOpenFileName(self.dlg, "Select file ","", '*.qml')
        self.dlg.lineEditStyle.setText(filename)
        
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        layers = QgsMapLayerRegistry.instance().mapLayers().values()
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

            QMessageBox.information(self.iface.mainWindow(),"hello world","%s has %d features." %(layerSurveys.name(),layerSurveys.featureCount()))
            crs = layerSupply.crs()

            # Set up indexes
            idxSurveyID = layerSurveys.fieldNameIndex('SurveyID')
            idxSurveyTime = layerSurveys.fieldNameIndex('SurveyTimePeriod')
            idxSurveyDay = layerSurveys.fieldNameIndex('SurveyDay')

            idxSupplySurveyID = layerSupply.fieldNameIndex('SurveyID')
            idxSupplySurveyDay = layerSupply.fieldNameIndex('SurveyDay')
            idxSupplySurveyTime = layerSupply.fieldNameIndex('SurveyTime')

            idxSupplyGeometry = layerSupply.fieldNameIndex('geom')

            dirname = self.dlg.lineEdit.text()
            dBname = self.dlg.lineEditDB.text()
            UIname = self.dlg.lineEditUI.text()
            StyleName = self.dlg.lineEditStyle.text()

            #dirname = ''
            #dBname = 'Z:/Tim/PC19-05 Burnham and Taplow, Buckinghamshire/Mapping/Spatialite/Test11.gpkg'
            #UIname = ''
            #StyleName = ''

            if len(dirname)>0:
                QgsMessageLog.logMessage("Shape file choosen ..." + str(dirname), tag="TOMs panel")

            if len(dBname)>0:
                # set up database links, etc
                uri = QgsDataSourceURI()
                uri.setDatabase(dBname)
                schema = ''
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName(uri.database())
                db.open()
                #conn = db.connect(dBname)

                QgsMessageLog.logMessage("Spatialite choosen:" + str(dBname) + ":" + str(layerSupply.name()),
                                     tag="TOMs panel")

                attr = layerSupply.fields().toList()

            featureSet = layerSurveys.getFeatures()
            idx = layerSurveys.fieldNameIndex('SurveyID')

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

                # Create shape file

                if len(dirname)>0:

                    QgsMessageLog.logMessage("Shape file choosen ...", tag="TOMs panel")

                    writer = QgsVectorFileWriter.writeAsVectorFormat(layerSupply,filePath,"utf-8",None,"ESRI Shapefile")
                    vlayer = QgsVectorLayer(filePath + ".shp", layerName, "ogr")
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer)

                    vlayer.startEditing()
                    for feat in vlayer.getFeatures():
                        vlayer.changeAttributeValue(feat.id(), idxSupplySurveyID, surveyID)
                        vlayer.changeAttributeValue(feat.id(), idxSupplySurveyDay, surveyDay)
                        vlayer.changeAttributeValue(feat.id(), idxSupplySurveyTime, surveyTime)

                    vlayer.commitChanges()

                elif len(dBname)>0:
                    #writer = QgsVectorFileWriter.writeAsVectorFormat(layerSupply,filePath,"utf-8",None,"ESRI Shapefile")
                    #vlayer = QgsVectorLayer(filePath + ".shp", layerName, "ogr")

                    QgsMessageLog.logMessage("Spatialite choosen ..." + str(dBname) + ":" + str(layerName), tag="TOMs panel")

                    crst = layerSupply.crs().toWkt()
                    newDemandLayer = QgsVectorLayer("LineString?crs=" + crst, layerName, "memory")
                    #newDemandLayer.setCrs(crs)
                    #newDemandLayer = QgsVectorLayer(layerSupply.source())
                    #newDemandLayer.setName(layerName)

                    #newDemandLayer.addAttributes(attr)
                    newDemandLayer.startEditing()

                    for field in attr:
                        newDemandLayer.addAttribute(field)
                        QgsMessageLog.logMessage("Adding field ..." + field.name(), tag="TOMs panel")
                    newDemandLayer.updateFields()
                    check = newDemandLayer.addFeatures(feats)

                    for feat in newDemandLayer.getFeatures():
                        newDemandLayer.changeAttributeValue(feat.id(), idxSupplySurveyID, surveyID)
                        newDemandLayer.changeAttributeValue(feat.id(), idxSupplySurveyDay, surveyDay)
                        newDemandLayer.changeAttributeValue(feat.id(), idxSupplySurveyTime, surveyTime)

                    newDemandLayer.commitChanges()

                    """try:
                        newDemandLayer = QgsVectorLayer(uri.database(), layerName, 'spatialite')

                    except:
                        QgsMessageLog.logMessage('creating layer', tag="TOMs panel")
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        QgsMessageLog.logMessage(
                            'creating layer: error: ' + str(
                                repr(traceback.extract_tb(exc_traceback))),
                            tag="TOMs panel")"""

                    #QgsMapLayerRegistry.instance().addMapLayer(newDemandLayer)

                    # https://gis.stackexchange.com/questions/285346/add-layers-to-geopackage-using-pyqgis-qgis-3?rq=1

                    errorMsg = ''
                    options = QgsVectorFileWriter.SaveVectorOptions()
                    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                    #options.ct = crs
                    #options.driverName = 'SQlite'
                    options.driverName = 'Geopackage'
                    #options.datasourceOptions = ["SPATIALITE=YES"]
                    #options.layerName = "_".join(lyr.name().split(' '))
                    error = QgsVectorFileWriter.writeAsVectorFormat(newDemandLayer, dBname, options)
                    """if error:
                        QMessageBox.information(self.iface.mainWindow(), "hello world",
                                                newDemandLayer.name() + ". Error number:" + str(error) + ":" + str(errorMsg))

                    error = QgsVectorFileWriter.writeAsVectorFormat(newDemandLayer,
                                                                    dBname,
                                                                    'System',
                                                                    crs,
                                                                    'SQLite',
                                                                    False,
                                                                    errorMsg,
                                                                    ["SPATIALITE=YES", ])"""

                    if error != QgsVectorFileWriter.NoError:
                        QMessageBox.information(self.iface.mainWindow(), "hello world",
                                                "Error number:" + str(error) + ":" + str(errorMsg))
                        #print 'Error number:', error
                        return
                    else:

                        """uri = QgsDataSourceUri()
                        uri.setDatabase(dBname)
                        schema = ''
                        table = layerSupply
                        geom_column = 'geom'
                        uri.setDataSource(schema, table, geom_column)

                        display_name = layerName
                        vlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')"""

                        #vlayer = QgsVectorLayer(uri.uri(), newDemandLayer.name(), 'Geopackage')

                        #QgsMapLayerRegistry.instance().addMapLayer(newDemandLayer)
                        #return

                else:
                    QMessageBox.information(self.iface.mainWindow(), "hello world",
                                            "No location choosen")
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

                
