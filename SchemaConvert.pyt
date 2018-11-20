import arcpy
import pandas

class Toolbox (object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "SchemaConvert"
        self.alias = "SchemaConvert"

        # List of tool classes associated with this toolbox
        self.tools = [DropFields,RenameFields,NullFields,PopulateMapUnitConfidence,BuildDataSources,BuildGlossary,]

class DropFields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "DropFields"
        self.description = "aasdasdsa"
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
                if field.name in listFieldToDrop:
                    arcpy.AddMessage("     >Dropped: " + field.name)
                    arcpy.DeleteField_management(fcpath, field.name)
                else:
                    arcpy.AddMessage("      Did not need to drop: " + field.name)
        arcpy.env.overwriteOutput = False

        return


class RenameFields(object):
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

class NullFields(object):
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

class BuildDataSources(object):
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
        # Inputs
        arcpy.env.overwriteOutput = True
        gdb = parameters[1].valueAsText
        arcpy.AddMessage(gdb)
        dataSourceFieldNames = ["DataSourceID", "LocationSourceID", "AnalysisSourceID", "OrientationSourceID", "DefinitionSourceID"]

        df2 = pandas.read_excel(parameters[0].valueAsText)
        # print(df2)
        master_DataSourceID = df2['FOLDERNAME'].values.tolist()
        master_Authors = df2['AUTHORS'].values.tolist()
        master_URL = df2['SOURCEURL'].values.tolist()
        master_Reference = df2['REFERENCE'].values.tolist()

        DataSourcesInMap = set([])
        arcpy.env.workspace = gdb
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
                        arcpy.AddMessage("      >" + str(fc) + " has field: " +field.name)
                        arcpy.Frequency_analysis(fc, "in_memory/freq", field.name)
                        with arcpy.da.SearchCursor("in_memory/freq", field.name) as cursor:
                            for row in cursor:
                                    DataSourcesInMap.add(row[0])

        # Make a copy of the reference table
        arcpy.AddMessage(parameters[2].valueAsText)
        arcpy.Copy_management(parameters[2].valueAsText, gdb + "\\" + "DataSources")

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
            elif dataSource <> "FGDC-STD-013-2006":
                arcpy.AddMessage("  >Data source: " + dataSource + " is NOT in the master. Update!!!")
                ForTable_MissingDataSources.append(dataSource)
            else:
                arcpy.AddMessage("   Data source: FGDC-STD-013-2006 being ignored")

        # Update the table
        # Assumes/requires GEMS field names
        cursor = arcpy.da.InsertCursor(gdb + "\\" + "DataSources", ['Source', 'URL', 'DataSources_ID'])
        for i, item in enumerate(ForTable_DataSources):
            cursor.insertRow([ForTable_Source[i], ForTable_URL[i], ForTable_DataSources[i]])
        del cursor

        if len(ForTable_MissingDataSources) > 0:
            # Add the missing datasourceIDs
            cursor2 = arcpy.da.InsertCursor(gdb + "\\" + "DataSources", ['DataSources_ID'])
            for x, item2 in enumerate(ForTable_MissingDataSources):
                cursor2.insertRow([ForTable_MissingDataSources[x]])
            del cursor2

        arcpy.env.overwriteOutput = False
        return

class BuildGlossary(object):
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
        # Inputs

        glossaryTable = parameters[0].valueAsText
        gdb = parameters[1].valueAsText

        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("Building Glossary table...")
        dfG = pandas.read_excel(glossaryTable)
        master_Terms = dfG['Term'].values.tolist()
        master_Definitions = dfG['Definition'].values.tolist()
        master_DefinitionSouces = dfG['DefinitionSourceID'].values.tolist()

        arcpy.env.workspace = gdb
        listFDSinGDB = arcpy.ListDatasets()
        TermsInMap = set([])

        for fds in listFDSinGDB:
            listFCsinFDS = arcpy.ListFeatureClasses(feature_dataset=fds)
            arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
            for fc in listFCsinFDS:
                Terms = ["Type","IdentityConfidence","ExistenceConfidence","ScientificConfidence","ParagraphStyle","AgeUnits"]  # Expand this to look for other needed Glossary Terms if Needed
                # Currently focused on finding "Type" in ContactsAndFaults
                for term in Terms:
                    if len(arcpy.ListFields(fc, term)) > 0:
                        arcpy.AddMessage(" " + str(fc) + " has field: " + term)
                        arcpy.Frequency_analysis(fc, "in_memory/freq", term)
                        with arcpy.da.SearchCursor("in_memory/freq", term) as cursor:
                            for row in cursor:
                                TermsInMap.add(row[0])

        # Make a copy of the reference table
        arcpy.Copy_management(parameters[2].valueAsText, gdb + "\\" + "Glossary")
        arcpy.DeleteRows_management(gdb + "\\" + "Glossary") #Empty the table
        # Create some blank lists for filling
        ForTable_Terms = []
        ForTable_Def = []
        ForTable_GSources = []
        ForTable_MissingTerms = []
        for terminmap in TermsInMap:
            if terminmap in master_Terms:
                arcpy.AddMessage("   Term: " + terminmap + " is in master!")
                index = master_Terms.index(terminmap)
                ForTable_Def.append(master_Definitions[index])
                ForTable_GSources.append(master_DefinitionSouces[index])
                ForTable_Terms.append(terminmap)
            else:
                arcpy.AddMessage("  >Term: " + terminmap + " is NOT in the master. Update!!!")
                ForTable_MissingTerms.append(terminmap)
        # Update the table
        # Assumes/requires GEMS field names
        cursor = arcpy.da.InsertCursor(gdb + "\\" + "Glossary",
                                       ['Term', 'Definition', 'DefinitionSourceID'])
        for i, item in enumerate(ForTable_Terms):
            cursor.insertRow([ForTable_Terms[i], ForTable_Def[i], ForTable_GSources[i]])
        del cursor

        if len(ForTable_MissingTerms) > 0:
            # Add the missing datasourceIDs
            cursor2 = arcpy.da.InsertCursor(gdb + "\\" + "Glossary", ['Term'])
            for x, item2 in enumerate(ForTable_MissingTerms):
                cursor2.insertRow([ForTable_MissingTerms[x]])
            del cursor2
        arcpy.env.overwriteOutput = False
        return

class PopulateMapUnitConfidence(object):
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