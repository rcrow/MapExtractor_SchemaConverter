import arcpy
import pandas

def parsenestedlists(str):
    templist = map(unicode.strip, str.split(","))
    list = []
    for item in templist:
        nested = item.split("|")
        list.append(nested)
    arcpy.AddMessage(list)
    return list

class Toolbox (object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "SchemaConvert"
        self.alias = "SchemaConvert"

        # List of tool classes associated with this toolbox
        self.tools = [dropFields, dropFieldsFromSpecific, renameFields, nullFields, buildDataSources, buildGlossary,
                      populateMapUnitConfidence, buildDMUFramework, geomorphUnitConverter, populateLabelFromFeatureLinks]

class dropFields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "DropFields"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Coma Delimited List of Fields:",
            name="listFieldsToDrop",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Feature Dataset:",
            name="fds",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction="Input")

        #TODO add optional parameter that allows for work on only specific FCs

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #Inputs
        arcpy.env.overwriteOutput = True
        fds = parameters[1].valueAsText

        listFieldToDrop = map(unicode.strip, parameters[0].valueAsText.split(","))

        arcpy.AddMessage(str(listFieldToDrop))
        arcpy.AddMessage("Dropping fields...")
        arcpy.env.workspace = fds
        listFCsinFDS = arcpy.ListFeatureClasses()
        arcpy.AddMessage(str(listFCsinFDS))
        for fc in listFCsinFDS:
            fcpath = fds + "\\" + fc
            arcpy.AddMessage("   Feature Class for field dropping: " + fc)
            fields = arcpy.ListFields(fcpath)
            for field in fields:
                # print(field.name)
                if field.name in listFieldToDrop:
                    arcpy.AddMessage("     >Dropped: " + field.name)
                    arcpy.DeleteField_management(fcpath, field.name)
                else:
                    arcpy.AddMessage("      Did not need to drop: " + field.name)
        arcpy.env.overwriteOutput = False
        return

class dropFieldsFromSpecific(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "DropFieldsFromSpecific"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Coma Delimited List of FCs to Drop Fields From:",
            name="listFCsToDropFldsFrom",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Coma and ""|"" Delimited List of Fields to Drop:",
            name="listFieldsToDrop",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #Inputs
        arcpy.env.overwriteOutput = True

        arcpy.AddMessage("Dropping specific fields...")

        listFCsToDropFldsFrom = map(unicode.strip, parameters[0].valueAsText.split(","))
        listFieldToDrop = parsenestedlists(parameters[1].valueAsText)
        gdb = parameters[2].valueAsText

        arcpy.env.workspace = gdb
        listFDSInGDB = arcpy.ListDatasets()
        #arcpy.AddMessage(listFDSInGDB)
        count=0
        for fds in listFDSInGDB:
            arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
            listFCsinFinalFDS3 = arcpy.ListFeatureClasses(feature_dataset=fds)
            #TODO look for topology in the fds, which might interfer with the renaming of the fields
            for fc in listFCsinFinalFDS3:
                if fc in listFCsToDropFldsFrom:
                    fcFullPath = gdb + "\\" + fds + "\\" + fc
                    # Note if you use different disable tracking field the following will have to be changes
                    arcpy.DisableEditorTracking_management(fcFullPath, "DISABLE_CREATOR", "DISABLE_CREATION_DATE",
                                                           "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
                    listfields = arcpy.ListFields(fcFullPath, listFieldToDrop[count])
                    if len(listfields) > 0:
                        arcpy.AddMessage("   >Removing fields from: " + fc)
                        for field in listFieldToDrop[count]:
                            arcpy.AddMessage("     >Removing field: " + str(field.name))
                        arcpy.DeleteField_management(fcFullPath, listFieldToDrop[count])
                    count=count+1
                else:
                    arcpy.AddMessage("    Ignoring: " + fc)
        arcpy.env.overwriteOutput = False
        return

class renameFields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "RenameFields"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Excel Table with Fieldnames:",
            name="fieldsToRenameTable",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Feature Dataset:",
            name="fds",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction="Input")

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs
        arcpy.env.overwriteOutput = True
        fds = parameters[1].valueAsText

        dfRename = pandas.read_excel(parameters[0].valueAsText)
        sdeFieldNames = dfRename['sdeField'].values.tolist()
        gemsFieldNames = dfRename['GEMSField'].values.tolist()

        arcpy.AddMessage("Renaming fields...")
        arcpy.env.workspace = fds
        listFCsinFDS = arcpy.ListFeatureClasses()
        arcpy.AddMessage(str(listFCsinFDS))
        for fc in listFCsinFDS:
            fcpath = fds + "\\" + fc
            arcpy.AddMessage("   Feature Class for field renaming: " + fc)
            fields = arcpy.ListFields(fcpath)
            for field in fields:
                # print(field.name)
                if field.name in sdeFieldNames:
                    newfieldname = gemsFieldNames[sdeFieldNames.index(field.name)]
                    arcpy.AlterField_management(fcpath, field.name,"zzzz")  # Without this simple case changes are not always recognized
                    arcpy.AlterField_management(fcpath, "zzzz", newfieldname)
                    arcpy.AddMessage("     >" + field.name + " renamed to: " + newfieldname)
                else:
                    arcpy.AddMessage("      Did not need to rename: " + field.name)
        arcpy.env.overwriteOutput = False

        return

class nullFields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "NullFields"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Coma Delimited List of Fields:",
            name="listFieldsToNull",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Feature Dataset:",
            name="fds",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction="Input")

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs
        arcpy.env.overwriteOutput = True
        fds = parameters[1].valueAsText

        listFieldToNull = map(unicode.strip, parameters[0].valueAsText.split(","))

        arcpy.AddMessage(str(listFieldToNull))
        arcpy.AddMessage("Drop fields...")
        arcpy.env.workspace = fds
        listFCsinFDS = arcpy.ListFeatureClasses()
        arcpy.AddMessage(str(listFCsinFDS))
        for fc in listFCsinFDS:
            fcpath = fds + "\\" + fc
            arcpy.AddMessage("   Feature Class for field dropping: " + fc)
            fields = arcpy.ListFields(fcpath)
            for field in fields:
                # print(field.name)
                if field.name in listFieldToNull:
                    cannull = field.isNullable
                    if cannull:
                        arcpy.AddMessage("     >Nulling: " + field.name)
                        arcpy.CalculateField_management(fc, field.name, "NULL")
                    else:
                        arcpy.AddMessage("      Can't null: " + field.name)
        arcpy.env.overwriteOutput = False
        return

class populateMapUnitConfidence(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "PopulateMapUnitConfidence"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Coma Delimited List of Feature Classes:",
            name="listFCsToWorkOn",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        params = [param0,param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs

        gdb = parameters[0].valueAsText
        comaListAsString=parameters[1].valueAsText
        if comaListAsString:
            listFCsToWorkOn = map(unicode.strip, comaListAsString.split(","))
        else:
            listFCsToWorkOn = ["MapUnitPoints", "MapUnitPolys"]
            arcpy.AddMessage("Using defaults values of MapUnitPoints and MapUnitPolys")


        arcpy.env.overwriteOutput = True
        print("Crosswalking polys and points...")

        arcpy.env.workspace = gdb
        listFDSInGDB = arcpy.ListDatasets()
        arcpy.AddMessage(listFDSInGDB)
        for fds in listFDSInGDB:
            arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
            listFCsinFinalFDS3 = arcpy.ListFeatureClasses(feature_dataset=fds)
            for fc in listFCsinFinalFDS3:
                arcpy.AddMessage("     Looking Through Feature Dataset: " + fc)
                fcpath3 = gdb + "\\" + fds + "\\" + fc
                # print(finalfc3)
                # print(fcpath3)
                if fc in listFCsToWorkOn:
                    arcpy.env.workspace = gdb
                    # print(arcpy.env.workspace)
                    edit = arcpy.da.Editor(arcpy.env.workspace)
                    edit.startEditing(False, True)
                    edit.startOperation()
                    with arcpy.da.UpdateCursor(fcpath3, ['MapUnit', 'IdentityConfidence']) as cursor3:
                        for row3 in cursor3:
                            if str(row3[0]).find("?") == -1:
                                row3[1] = "certain"
                            # elif str(row3[0]).find("/") == -1:
                            #     row3[1] = "interbedded"
                            else:
                                row3[1] = "questionable"
                            cursor3.updateRow(row3)
                    edit.stopOperation()
                    edit.stopEditing(True)
        arcpy.env.overwriteOutput = False

class buildDMUFramework(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "BuildDMUFramework"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Excel Table with Master List of MapUnits:",
            name="MasterMapUnitTable",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="DMU Table Template:",
            name="exampleBlankDMUTable",
            datatype="DETable",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Null Description Field",
            name="NullDescription",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Null Areal Fill Pattern Description Field",
            name="NullPattern",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Calculate IDs",
            name="calcIDs",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="DescriptionSourceID for all entries:",
            name="descSourceID",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        params = [param0, param1, param2,param3,param4,param5,param6]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs

        masterDMUTable = parameters[0].valueAsText
        gdb = parameters[1].valueAsText
        nullDescription = parameters[3].valueAsText
        arcpy.AddMessage(nullDescription)
        nullFillPattern = parameters[4].valueAsText
        arcpy.AddMessage(nullFillPattern)
        calcIDs = parameters[5].valueAsText
        descSourceID =parameters[6].valueAsText
        # arcpy.AddMessage(descSourceID)
        # arcpy.AddMessage(type(descSourceID))

        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("Building DMU table...")
        dfG = pandas.read_excel(masterDMUTable)
        header=list(dfG.columns.values)

        master_MapUnit = dfG['MapUnit'].values.tolist()
        master_UnitName = dfG['Name'].values.tolist()
        master_Age = dfG['Age'].values.tolist()
        master_Description = dfG['Description'].values.tolist()
        master_FullName = dfG['FullName'].values.tolist()
        master_Order = dfG['DMUOrder'].values.tolist()
        master_ParagraphStyle = dfG['ParagraphStyle'].values.tolist()
        master_Label = dfG['Label'].values.tolist()
        master_Symbol = dfG['Symbol'].values.tolist()
        master_AreaFillRGB = dfG['AreaFillRGB'].values.tolist()
        master_AreaFillPatternDescription = dfG['AreaFillPatternDescription'].values.tolist()
        master_GeoMaterial = dfG['GeoMaterial'].values.tolist()
        master_GeoMConfidence = dfG['GeoMaterialConfidence'].values.tolist()

        arcpy.env.workspace = gdb
        listFDSinGDB = arcpy.ListDatasets()
        MapUnitsInMap = set([])

        for fds in listFDSinGDB:
            listFCsinFDS = arcpy.ListFeatureClasses(feature_dataset=fds)
            arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
            for fc in listFCsinFDS:
                arcpy.AddMessage("      Looking Through Feature Class: " + fc)
                Terms = ["MapUnit"]  # Expand this to look for other needed Glossary Terms if Needed
                # Currently focused on finding "Type" in ContactsAndFaults
                for term in Terms:
                    if len(arcpy.ListFields(fc, term)) > 0:
                        arcpy.AddMessage("        " + str(fc) + " has field: " + term)
                        arcpy.Frequency_analysis(fc, "in_memory/freq", term)
                        with arcpy.da.SearchCursor("in_memory/freq", term) as cursor:
                            for row in cursor:
                                MapUnitsInMap.add(row[0])

        # arcpy.AddMessage(str(MapUnitsInMap))
        # Make a copy of the reference table

        DMUTablePath = gdb + "\\" + "DescriptionOfMapUnits"
        arcpy.Copy_management(parameters[2].valueAsText, DMUTablePath)
        #arcpy.DeleteRows_management(gdb + "\\" + "Glossary")  # Empty the table
        # Create some blank lists for filling
        ForTable_MapUnit = []
        ForTable_UnitName = []
        ForTable_Age = []
        ForTable_Description = []
        ForTable_FullName = []
        ForTable_Order = []
        ForTable_MissingMapUnit = []
        ForTable_ParagraphStyle = []
        ForTable_Label = []
        ForTable_Symbol = []
        ForTable_AreaFillRGB = []
        ForTable_AreaFillPatternDescription = []
        ForTable_GeoMaterial = []
        ForTable_GeoMaterialConfidence = []

        for mapunit in MapUnitsInMap:
            if mapunit in master_MapUnit:
                arcpy.AddMessage("   Term: " + mapunit + " is in master!")
                index = master_MapUnit.index(mapunit)
                ForTable_Age.append(master_Age[index])
                ForTable_Description.append(master_Description[index])
                ForTable_UnitName.append(master_UnitName[index])
                ForTable_MapUnit.append(mapunit)
                ForTable_FullName.append(master_FullName[index])
                ForTable_Order.append(master_Order[index])
                ForTable_ParagraphStyle.append(master_ParagraphStyle[index])
                ForTable_Label.append(master_Label[index])
                ForTable_Symbol.append(master_Symbol[index])
                ForTable_AreaFillRGB.append(master_AreaFillRGB[index])
                ForTable_AreaFillPatternDescription.append(master_AreaFillPatternDescription[index])
                ForTable_GeoMaterial.append(master_GeoMaterial[index])
                ForTable_GeoMaterialConfidence.append(master_GeoMConfidence[index])
            else:
                if mapunit is not None:
                    arcpy.AddMessage("  >Term: " + mapunit + " is NOT in the master. Update!!!")
                    ForTable_MissingMapUnit.append(mapunit)
                else:
                    arcpy.AddMessage("Null mapunit!")

        # arcpy.AddMessage(ForTable_Description)
        # arcpy.AddMessage(ForTable_AreaFillRGB)
        # arcpy.AddMessage(ForTable_AreaFillPatternDescription)
        # Update the table
        # Assumes/requires GEMS field names
        #arcpy.AddField_management(gdb + "\\" + "DescriptionOfMapUnits","TempOrder","Integer")
        cursor = arcpy.da.InsertCursor(DMUTablePath,
                                       ['MapUnit', 'Name', 'Age','Description','FullName','HierarchyKey','ParagraphStyle','Label',
                                        'Symbol','AreaFillRGB','AreaFillPatternDescription','GeoMaterial','GeoMaterialConfidence'])
        for i, item in enumerate(ForTable_MapUnit):
            cursor.insertRow([ForTable_MapUnit[i], ForTable_UnitName[i], ForTable_Age[i], ForTable_Description[i],
                              ForTable_FullName[i], ForTable_Order[i], ForTable_ParagraphStyle[i], ForTable_Label[i],
                              ForTable_Symbol[i], ForTable_AreaFillRGB[i], ForTable_AreaFillPatternDescription[i],
                              ForTable_GeoMaterial[i], ForTable_GeoMaterialConfidence[i]
                              ])
        del cursor

        if len(ForTable_MissingMapUnit) > 0:
            # Add the missing datasourceIDs
            cursor2 = arcpy.da.InsertCursor(DMUTablePath, ['MapUnit'])
            for x, item2 in enumerate(ForTable_MissingMapUnit):
                cursor2.insertRow([ForTable_MissingMapUnit[x]])
            del cursor2

        if nullDescription:
            arcpy.AddMessage("Nulling the Description field...")
            arcpy.CalculateField_management(DMUTablePath, 'Description', "NULL")

        if nullFillPattern:
            arcpy.AddMessage("Nulling the AreaFillPatternDescription field...")
            arcpy.CalculateField_management(DMUTablePath, 'AreaFillPatternDescription', "NULL")

        if calcIDs:
            arcpy.AddMessage("Calculating DescriptionOfMapUnits IDs...")
            arcpy.CalculateField_management(DMUTablePath,'DescriptionOfMapUnits_ID',"\"DMU\"&[OBJECTID]")

        if isinstance(descSourceID, unicode):
            arcpy.AddMessage("Assigning Source IDs...")
            arcpy.CalculateField_management(DMUTablePath,'DescriptionSourceID',"\""+descSourceID+"\"")

        arcpy.env.overwriteOutput = False
        return

class buildDataSources(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "BuildDataSources"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Excel Table with Master List of DataSource Info:",
            name="masterDataSourcesTable",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="DataSources Table Template:",
            name="exampleBlankDataSourceTable",
            datatype="DETable",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Only Build Based on Non-Spatial Tables",
            name="onlyTables",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs
        arcpy.env.overwriteOutput = True
        gdb = parameters[1].valueAsText
        onlyTables = parameters[3].valueAsText
        arcpy.AddMessage(gdb)
        dataSourceFieldNames = ["DataSourceID", "LocationSourceID", "AnalysisSourceID", "OrientationSourceID",
                                "DefinitionSourceID"]

        df2 = pandas.read_excel(parameters[0].valueAsText)
        # print(df2)
        master_DataSourceID = df2['FOLDERNAME'].values.tolist()
        master_Authors = df2['AUTHORS'].values.tolist()
        master_URL = df2['SOURCEURL'].values.tolist()
        master_Reference = df2['REFERENCE'].values.tolist()

        DataSourcesInMap = set([])
        arcpy.env.workspace = gdb
        if onlyTables:
            arcpy.AddMessage("   Looking Through Tables Only")
            listTablesinGDB = arcpy.ListTables()
            arcpy.AddMessage(listTablesinGDB)
            for table in listTablesinGDB:
                tablepath = gdb + "\\" +  table
                arcpy.AddMessage("    Looking Through Table: " + table)
                fields = arcpy.ListFields(tablepath)
                for field in fields:
                    arcpy.AddMessage("     Considering field: " + field.name)
                    if field.name in dataSourceFieldNames:
                        arcpy.AddMessage("    >" + str(table) + " has field: " + field.name)
                        arcpy.Frequency_analysis(table, "in_memory/freq", field.name)
                        with arcpy.da.SearchCursor("in_memory/freq", field.name) as cursor:
                            for row in cursor:
                                arcpy.AddMessage("        Field: " + str(row[0]))
                                DataSourcesInMap.add(row[0])
        else:
            listFDSinGDB = arcpy.ListDatasets()
            for fds in listFDSinGDB:
                listFCsinFDS = arcpy.ListFeatureClasses(feature_dataset=fds)
                arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
                for fc in listFCsinFDS:
                    fcpath = gdb + "\\" + fds + "\\" + fc
                    arcpy.AddMessage("    Looking Through Feature Class: " + fc)
                    fields = arcpy.ListFields(fcpath)
                    for field in fields:
                        arcpy.AddMessage("     Considering field: " + field.name)
                        if field.name in dataSourceFieldNames:
                            arcpy.AddMessage("    >" + str(fc) + " has field: " + field.name)
                            arcpy.Frequency_analysis(fc, "in_memory/freq", field.name)
                            with arcpy.da.SearchCursor("in_memory/freq", field.name) as cursor:
                                for row in cursor:
                                    DataSourcesInMap.add(row[0])

        # Make a copy of the reference table
        templateTable = parameters[2].valueAsText

        if templateTable:
            arcpy.Copy_management(templateTable, gdb + "\\" + "DataSources")

        # Create some blank lists for filling
        ForTable_Source = []
        ForTable_URL = []
        ForTable_DataSources = []
        ForTable_MissingDataSources = []
        for dataSource in DataSourcesInMap:
            # This assumes that FGDC-STD-013-2006 will be in the table when it's copied over - don't put it in again
            if dataSource in master_DataSourceID and dataSource <> "FGDC-STD-013-2006":
                arcpy.AddMessage("   Data source: " + dataSource + " is in master!")
                index = master_DataSourceID.index(dataSource)
                ForTable_Source.append(master_Reference[index])
                ForTable_URL.append(master_URL[index])
                ForTable_DataSources.append(dataSource)
            elif dataSource <> "FGDC-STD-013-2006" and not None:
                arcpy.AddMessage("  >Data source: " + dataSource + " is NOT in the master. Update!!!")
                ForTable_MissingDataSources.append(dataSource)
            elif dataSource is None or dataSource == "" or dataSource == " ":
                arcpy.AddMessage("Null datasource")
            elif dataSource == "FGDC-STD-013-2006":
                arcpy.AddMessage("   Data source: FGDC-STD-013-2006 being ignored")
            else:
                arcpy.AddMessage("## Warning unexpected condition meet ##")

        # Update the table
        # Assumes/requires GEMS field names
        coreFieldNames = ['Source', 'URL', 'DataSources_ID']
        cursor = arcpy.da.InsertCursor(gdb + "\\" + "DataSources", coreFieldNames)
        for i, item in enumerate(ForTable_DataSources):
            cursor.insertRow([ForTable_Source[i], ForTable_URL[i], ForTable_DataSources[i]])
        del cursor

        if len(ForTable_MissingDataSources) > 0:
            # Add the missing datasourceIDs
            cursor2 = arcpy.da.InsertCursor(gdb + "\\" + "DataSources", ['DataSources_ID'])
            for x, item2 in enumerate(ForTable_MissingDataSources):
                cursor2.insertRow([ForTable_MissingDataSources[x]])
            del cursor2

        arcpy.DeleteIdentical_management(gdb + "\\" + "DataSources", coreFieldNames) #This is needed if the tool has to run muliple times on a db
        arcpy.env.overwriteOutput = False
        return

class buildGlossary(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "BuildGlossary"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Excel Table with Master List of Terms and Definitions:",
            name="glossaryTable",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Glossary Table Template:",
            name="exampleBlankGlossaryTable",
            datatype="DETable",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Only Build Based on Non-Spatial Tables",
            name="onlyTables",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        params = [param0, param1, param2 , param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs

        glossaryTable = parameters[0].valueAsText
        gdb = parameters[1].valueAsText
        onlyTables = parameters[3].valueAsText
        templateTable = parameters[2].valueAsText

        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("Building Glossary table...")
        dfG = pandas.read_excel(glossaryTable)
        master_Terms = dfG['Term'].values.tolist()
        master_Definitions = dfG['Definition'].values.tolist()
        master_DefinitionSouces = dfG['DefinitionSourceID'].values.tolist()

        arcpy.env.workspace = gdb
        listFDSinGDB = arcpy.ListDatasets()
        TermsInMap = set([])
        Terms = ["Type", "IdentityConfidence", "ExistenceConfidence", "ScientificConfidence", "ParagraphStyle",
                 "GeoMaterialConfidence", "Scale", "AgeUnits","OrigUnit"]
        if onlyTables == 'true':
            arcpy.AddMessage("  Looking Through Tables Only")
            listTablesinGDB = arcpy.ListTables()
            # arcpy.AddMessage(listTablesinGDB)
            #TODO The code block below is repreated consider wrapping in a fucntion
            for table in listTablesinGDB:
                if table not in ['Glossary','GeoMaterialDict']:
                    arcpy.AddMessage("   Looking Through Table: " + str(table))
                    for term in Terms:
                        #arcpy.AddMessage(arcpy.ListFields(table, term))
                        if len(arcpy.ListFields(table, term)) > 0:
                            arcpy.AddMessage("    -" + str(table) + " has field: " + term)
                            arcpy.Frequency_analysis(table, "in_memory/freq", term)
                            with arcpy.da.SearchCursor("in_memory/freq", term) as cursor:
                                for row in cursor:
                                    TermsInMap.add(row[0])
                        else:
                            arcpy.AddMessage("    " + term + " not in the table")
                else:
                    arcpy.AddMessage("   Ignoring Table: " + str(table))
        else:
            for fds in listFDSinGDB:
                arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
                listFCsinFDS = arcpy.ListFeatureClasses(feature_dataset=fds)
                for fc in listFCsinFDS:
                    # Currently focused on finding "Type" in ContactsAndFaults
                    for term in Terms:
                        if len(arcpy.ListFields(fc, term)) > 0:
                            arcpy.AddMessage(" " + str(fc) + " has field: " + term)
                            arcpy.Frequency_analysis(fc, "in_memory/freq", term)
                            with arcpy.da.SearchCursor("in_memory/freq", term) as cursor:
                                for row in cursor:
                                    TermsInMap.add(row[0])
        arcpy.AddMessage(TermsInMap)

        # Make a copy of the reference table only if it is not already in the gdb
        if templateTable:
            arcpy.Copy_management(templateTable, gdb + "\\" + "Glossary")
            arcpy.DeleteRows_management(gdb + "\\" + "Glossary")  # Empty the table
        # Create some blank lists for filling
        ForTable_Terms = []
        ForTable_Def = []
        ForTable_GSources = []
        ForTable_MissingTerms = []
        for terminmap in TermsInMap:
            if terminmap:
                if terminmap in master_Terms:
                    arcpy.AddMessage("   Term: " + terminmap + " is in master!")
                    index = master_Terms.index(terminmap)
                    ForTable_Def.append(master_Definitions[index])
                    ForTable_GSources.append(master_DefinitionSouces[index])
                    ForTable_Terms.append(terminmap)
                else:
                    arcpy.AddMessage("  >Term: " + terminmap + " is NOT in the master. Update!!!")
                    ForTable_MissingTerms.append(terminmap)
            else:
                arcpy.AddMessage("WARNING blank glossary value")
        # Update the table
        # Assumes/requires GEMS field names
        coreFields=['Term', 'Definition', 'DefinitionSourceID']
        cursor = arcpy.da.InsertCursor(gdb + "\\" + "Glossary",coreFields)
        for i, item in enumerate(ForTable_Terms):
            cursor.insertRow([ForTable_Terms[i], ForTable_Def[i], ForTable_GSources[i]])
        del cursor

        if len(ForTable_MissingTerms) > 0:
            # Add the missing datasourceIDs
            cursor2 = arcpy.da.InsertCursor(gdb + "\\" + "Glossary", ['Term'])
            for x, item2 in enumerate(ForTable_MissingTerms):
                cursor2.insertRow([ForTable_MissingTerms[x]])
            del cursor2
        arcpy.DeleteIdentical_management(gdb + "\\" + "Glossary",coreFields) #This is needed if the tool has to run muliple times on a db
        arcpy.env.overwriteOutput = False
        return

class geomorphUnitConverter(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GeomorphUnitConverter"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Feature class:",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Field containing the composit unit: ",
            name="independent",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs

        fc = parameters[0].valueAsText
        independent = parameters[1].valueAsText
        arcpy.env.overwriteOutput = True
        fieldsToAdd = ["mapunit","underunit","interlacedunit","compositeunit"]
        for field in fieldsToAdd:
            arcpy.AddField_management(in_table=fc,field_name=field,field_type="TEXT",field_length=50)

        fields= [independent]+fieldsToAdd

        with arcpy.da.UpdateCursor(fc, fields) as cursor:
            count = 1
            for row in cursor:
                slashes = row[0].count("/")
                pluses = row[0].count("+")
                arcpy.AddMessage("Feature #" + str(count) + " has " + str(slashes) + " Slashes and " + str(pluses) + " Pluses")
                if (slashes > 0 and pluses == 0):
                    parts = row[0].split("/")
                    row[1] = parts[0]
                    row[2] = parts[1]
                    row[4] = row[0]
                elif (pluses > 0 and slashes == 0):
                    parts = row[0].split("+")
                    row[1] = parts[0]
                    row[3] = parts[1]
                    row[4] = row[0]
                elif (pluses == 0 and slashes == 0):
                    row[1] = row[0]
                    row[4] = row[0]
                cursor.updateRow(row)
                count = count + 1
        arcpy.env.overwriteOutput = False
        return

class populateLabelFromFeatureLinks(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "PopulateLabelFromFeatureLinks"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Feature Dataset in the GDB:",
            name="fds",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Coma Delimited List of Feature-linked Annotation Feature Classes:",
            name="annos",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Coma Delimited List of Feature Classes linked to the Annotations:",
            name="fcs",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Null the label field first",
            name="nullFirst",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")


        params = [param0, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Inputs

        #TODO get gdb that the fds is in from path
        gdb = parameters[0].valueAsText
        fds = parameters[1].valueAsText
        listFCs = map(unicode.strip, parameters[2].valueAsText.split(","))
        listAnnos = map(unicode.strip, parameters[3].valueAsText.split(","))
        nullFirst = parameters[4].valueAsText
        print("Null first: "+ nullFirst)

        arcpy.env.overwriteOutput = True
        print("Populating the Label field from the feature-linked annotations...")
        arcpy.env.workspace = gdb
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(False, True)
        edit.startOperation()
        #Note assumes lowercase field names
        for i, anno in enumerate(listAnnos):
            annoPath = fds + "\\" + anno
            with arcpy.da.SearchCursor(annoPath,
                                       ["featureid", "textstring"]) as cursor:  # Note lowercase names from postgres
                listFeatureIds = []
                listLabels = []
                for row in cursor:
                    listFeatureIds.append(row[0])
                    listLabels.append(row[1])
            fcPath = fds + "\\" + listFCs[i]
            if nullFirst:
                arcpy.CalculateField_management(fcPath, "label", "NULL")
            with arcpy.da.UpdateCursor(fcPath, ["objectid", "label"]) as editcursor:
                for editrow in editcursor:
                    if editrow[0] in listFeatureIds:
                        index = listFeatureIds.index(editrow[0])
                        editrow[1] = listLabels[index]
                        editcursor.updateRow(editrow)
        edit.stopOperation()
        edit.stopEditing(True)
        arcpy.env.overwriteOutput = False

        return