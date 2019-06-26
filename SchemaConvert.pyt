import arcpy
import datetime

def parsenestedlists(str):
    templist = map(unicode.strip, str.split(","))
    list = []
    for item in templist:
        nested = item.split("|")
        list.append(nested)
    arcpy.AddMessage(list)
    return list


def datetimePrint():
    time = datetime.datetime.now()  # Get system time
    if len(str(time.month)) == 1:
        month = "0" + str(time.month)
    else:
        month = str(time.month)
    if len(str(time.day)) == 1:
        day = "0" + str(time.day)
    else:
        day = str(time.day)
    if len(str(time.hour)) == 1:
        hour = "0" + str(time.hour)
    else:
        hour = str(time.hour)
    if len(str(time.minute)) == 1:
        minute = "0" + str(time.minute)
    else:
        minute = str(time.minute)
    if len(str(time.second)) == 1:
        second = "0" + str(time.second)
    else:
        second = str(time.second)
    timeDateString = str(time.year) + month + day + "_" + hour + minute + "_" + second
    date = month + "/" + day + "/" + str(time.year)
    timestr = hour + ":" + minute
    return [timeDateString, date, timestr, time]


class Toolbox (object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "SchemaConvert"
        self.alias = "SchemaConvert"

        # List of tool classes associated with this toolbox
        self.tools = [dropFields, dropFieldsFromSpecific, renameFields, nullFields, geomorphUnitConverter,
                      switchSymbolAndType, populateLabelFromFeatureLinks, populateMapUnitConfidence,simplifyHierarcyKeys,
                      alacarteToGeMS,nbmgToGeMS]

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

        for fds in listFDSInGDB:
            arcpy.AddMessage("   Looking Through Feature Dataset: " + fds)
            listFCsinFinalFDS3 = arcpy.ListFeatureClasses(feature_dataset=fds)
            #TODO look for topology in the fds, which might interfer with the renaming of the fields
            count = 0
            for fc in listFCsinFinalFDS3:
                if fc in listFCsToDropFldsFrom:
                    fcFullPath = gdb + "\\" + fds + "\\" + fc
                    # Note if you use different disable tracking field the following will have to be changes
                    arcpy.DisableEditorTracking_management(fcFullPath, "DISABLE_CREATOR", "DISABLE_CREATION_DATE",
                                                           "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
                    listfields = arcpy.ListFields(fcFullPath, listFieldToDrop[count])
                    fieldNamesinFC = [x.name for x in listfields]
                    print(fieldNamesinFC)
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
        import pandas

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

class switchSymbolAndType(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "SwitchSymbolAndType"
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
            displayName="Coma Delimited List of FCs to switch Symbol and Type in:",
            name="listFCsSwitchTypeAndSymbol",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Null symbol afterwards?",
            name="nullSymbol",
            datatype="Boolean",
            parameterType="Optional",
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
        gdb = parameters[0].valueAsText
        lisFCsToSwitch = map(unicode.strip, parameters[1].valueAsText.split(","))
        arcpy.AddMessage(lisFCsToSwitch)
        nullType = parameters[2].valueAsText
        print(nullType)
        arcpy.env.workspace = gdb
        listFDSinGDB = arcpy.ListDatasets()
        for fds in listFDSinGDB:
            listFCsinFDS = arcpy.ListFeatureClasses(feature_dataset=fds)
            arcpy.AddMessage("  Looking Through Feature Dataset: " + fds)
            for fc in listFCsinFDS:
                arcpy.AddMessage("    Looking Through Feature Class: " + fc)
                if fc in lisFCsToSwitch:
                    arcpy.AddMessage("      Switching Type to Symbol for: " + fc)
                    arcpy.CalculateField_management(fc, "Symbol", "[Type]")
                    if nullType:
                        arcpy.CalculateField_management(fc, "Type", "\"\"")
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
        fieldsToAdd = ["mapunit","underunit","interlacedunit","compositeunit","bedrockunit","underunderunit","underinterlaced"]
        for field in fieldsToAdd:
            arcpy.AddField_management(in_table=fc,field_name=field,field_type="TEXT",field_length=50)

        fields= [independent]+fieldsToAdd

        with arcpy.da.UpdateCursor(fc,fields) as cursor:
            count = 1
            for row in cursor:
                print(row[0])
                slashes = row[0].count("/")
                slashesIndex = row[0].find("/")
                print(slashesIndex)
                pluses = row[0].count("+")
                plusesIndex = row[0].find("+")
                print(plusesIndex)
                minuses = row[0].count("-")
                minusesIndex = row[0].find("-")
                print(minusesIndex)

                print("Feature #" + str(count) + " has " + str(slashes) + " Slashes and " + str(
                    pluses) + " Pluses and " + str(minuses) + " Minuses")
                # Case 2 only one stacked (e.g. Qyag/Qiag)
                if (slashes == 1 and pluses == 0 and minuses == 0):
                    print(" One Slash")
                    parts = row[0].split("/")
                    row[1] = parts[0]
                    row[2] = parts[1]
                    row[4] = row[0]
                # Case 1 only one interlacing (e.g. Qaa+Qyay)
                elif (pluses == 1 and slashes == 0 and minuses == 0):
                    print(" One Plus")
                    parts = row[0].split("+")
                    row[1] = parts[0]
                    row[3] = parts[1]
                    row[4] = row[0]
                # Case 3 only one pediment (e.g. Qpd-fpg)
                elif (minuses == 1 and pluses == 0 and slashes == 0):
                    print(" One Minus")
                    parts = row[0].split("-")
                    row[1] = parts[0]
                    row[5] = parts[1]
                    row[4] = row[0]
                # Case 4 interlaced over one unit
                elif (pluses == 1 and slashes == 1 and minuses == 0 and plusesIndex < slashesIndex):
                    print(" Plus before Slash")
                    parts = row[0].split("+")
                    secondParts = parts[1].split("/")
                    row[1] = parts[0]
                    row[3] = secondParts[0]
                    row[2] = secondParts[1]
                    row[4] = row[0]
                # Case 5 interlaced over pediment
                elif (pluses == 1 and slashes == 1 and minuses == 1 and plusesIndex < slashesIndex and slashesIndex < minusesIndex):
                    print(" Plus, Slash, and Minus in that order")
                    parts = row[0].split("/")
                    firstParts = parts[0].split("+")
                    secondParts = parts[1].split("-")
                    row[1] = firstParts[0]
                    row[3] = firstParts[1]
                    row[2] = secondParts[0]
                    row[5] = secondParts[1]
                    row[4] = row[0]
                # Case 6 three stacked
                elif (pluses == 0 and slashes == 2 and minuses == 0):
                    print(" 2 slashes")
                    parts = row[0].split("/")
                    row[1] = parts[0]
                    row[2] = parts[1]
                    row[6] = parts[2]
                    row[4] = row[0]
                # Case 7 interlaced under one unit
                elif (pluses == 1 and slashes == 1 and minuses == 0 and slashesIndex < plusesIndex):
                    print(" Plus before Slash")
                    parts = row[0].split("/")
                    secondParts = parts[1].split("+")
                    row[1] = parts[0]
                    row[2] = secondParts[0]
                    row[7] = secondParts[1]
                    row[4] = row[0]
                elif (pluses == 0 and slashes == 0 and minuses == 0):
                    row[1] = row[0]
                    row[4] = row[0]
                cursor.updateRow(row)
                count = count + 1
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
            displayName="Coma Delimited List of Feature Classes linked to the Annotations:",
            name="fcs",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Coma Delimited List of Feature-linked Annotation Feature Classes:",
            name="annos",
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
        arcpy.AddMessage("Populating the Label field from the feature-linked annotations...")
        arcpy.env.workspace = gdb
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(False, True)
        edit.startOperation()
        for i, anno in enumerate(listAnnos):
            annoPath = fds + "\\" + anno
            arcpy.AddMessage(annoPath)
            #Code to handle uppercase and lowercase field names
            #TODO this block needs testing
            fields = arcpy.ListFields(annoPath)
            fieldNames = [x.name for x in fields]
            if "FEATUREID" in fieldNames or "FeatureID" in fieldNames:
                Annofields = ["FEATUREID", "TextString"]
                FCfields = ["OBJECTID", "Label"]
            elif "featureid" in fieldNames:
                Annofields = ["featureid", "textstring"]
                FCfields = ["objectid", "label"]
            with arcpy.da.SearchCursor(annoPath,
                                       Annofields) as cursor:
                listFeatureIds = []
                listLabels = []
                for row in cursor:
                    listFeatureIds.append(row[0])
                    listLabels.append(row[1])
            fcPath = fds + "\\" + listFCs[i]
            if nullFirst:
                arcpy.CalculateField_management(fcPath, "label", "NULL")
            with arcpy.da.UpdateCursor(fcPath, FCfields) as editcursor:
                for editrow in editcursor:
                    if editrow[0] in listFeatureIds:
                        index = listFeatureIds.index(editrow[0])
                        editrow[1] = listLabels[index]
                        editcursor.updateRow(editrow)
        edit.stopOperation()
        edit.stopEditing(True)
        arcpy.env.overwriteOutput = False

        return

class simplifyHierarcyKeys(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "SimplifyHierarcyKeys"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="DMU Table:",
            name="table",
            datatype="DETable",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Output Geodatabase:",
            name="gdb",
            datatype="DEWorkspace",
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

        timeDateString = datetimePrint()[0]  # Gets time and date to add to export

        table = parameters[0].valueAsText
        gdb = parameters[1].valueAsText

        outputFullPath = gdb+"\\DMU_sorted_temp"

        # arcpy.Copy_management(DMUinputPath,outputFullPath)
        arcpy.Sort_management(table, outputFullPath, "HierarchyKey")

        previousOrigCode = ["000", "000", "000", "000", "000"]
        previousNewCode = ["000", "000", "000", "000", "000"]
        with arcpy.da.UpdateCursor(outputFullPath, ["HierarchyKey"]) as cursor:
            for row in cursor:
                currentCode = row[0].split("-")
                print("----------")
                print(" Previous orig Code: " + '-'.join(previousOrigCode))
                print(" Previous new Code: " + '-'.join(previousNewCode))
                print(" Current Code:  " + '-'.join(currentCode))
                newCode = ["000", "000", "000", "000", "000"]
                for position, item in enumerate(currentCode):
                    print("   Position: " + str(position))
                    print(item)
                    print(previousOrigCode[position])
                    if str(item) == str(previousOrigCode[position]):
                        print("    SAME")
                        newCode[position] = previousNewCode[position]
                        print(newCode[position])
                    elif item > previousOrigCode[position]:
                        print("    HIT")
                        newCode[position] = str(int(previousNewCode[position]) + 1).zfill(3)
                        for x in range(position + 1, 5):
                            print("     Zeroing out position: " + str(x))
                            newCode[x] = "000"
                    else:
                        print("    PROBLEM")
                print(" New Code:  " + '-'.join(newCode))
                previousOrigCode = currentCode
                previousNewCode = newCode
                row[0] = ('-'.join(newCode))
                cursor.updateRow(row)
        arcpy.env.overwriteOutput = True
        arcpy.Copy_management(outputFullPath, gdb+"\\DescriptionOfMapUnits_Sorted")
        arcpy.Delete_management(table)
        arcpy.Delete_management(outputFullPath)
        arcpy.Rename_management(gdb+"\\DescriptionOfMapUnits_Sorted",table)
        arcpy.env.overwriteOutput = True

class alacarteToGeMS(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "AlacarteToGeMS"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Workspace:",
            name="workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="DB name:",
            name="dbName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="MapUnitPolys features:",
            name="polys",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="ContactsAndFaults features:",
            name="arcs",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="GEMS toolbox:",
            name="GEMS toolbox",
            datatype="Toolbox",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Crosswalk Table:",
            name="crosswalk table",
            datatype="DETextFile",
            parameterType="Optional",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="DataSourceID for this map:",
            name="datasource",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Label field name in MapUnitPolys:",
            name="labelname",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        params = [param0,param1,param2,param3,param4,param5,param6,param7]
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
        # This is yet to be created ...

        import os

        pathToWorkspace = parameters[0].valueAsText
        dbName= parameters[1].valueAsText
        MapUnitPolys = parameters[2].valueAsText
        ContactsAndFaults = parameters[3].valueAsText
        toolbox = parameters[4].valueAsText
        toolbox2 = os.path.abspath(__file__)
        crosswalk = parameters[5].valueAsText
        datasource = parameters[6].valueAsText
        labelname = parameters[7].valueAsText

        #This will only work for users on our network
        arcpy.ImportToolbox(toolbox)
        arcpy.ImportToolbox(toolbox2)
        arcpy.env.overwriteOutput = True
        # Create a new GDB
        timeDateString = datetimePrint()[0] # Gets time and date to add to export
        print(" Current Run: " + timeDateString)
        arcpy.AddMessage("Creating a GDB")

        #TODO the spatial reference frame is hardcoded
        arcpy.CreateDatabase_GEMS(Output_Workspace=pathToWorkspace,
                                  Name_of_new_geodatabase=dbName,
                                  Spatial_reference_system="PROJCS['NAD_1983_UTM_Zone_11N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-117.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
                                  Optional_feature_classes__tables__and_feature_datasets="",
                                  Number_of_cross_sections="0",
                                  Enable_edit_tracking="true",
                                  Add_fields_for_cartographic_representations="false",
                                  Add_LTYPE_and_PTTYPE="true",
                                  Add_standard_confidence_values="true")

        gdbPath=pathToWorkspace+"\\"+dbName+".gdb"


        #MapUnitPolys
        arcpy.AddMessage("Adding the MapUnitPolys")

        target_layer = gdbPath+"\\"+"GeologicMap"+"\\"+"MapUnitPolys"
        target_field = "Label"
        #listTargetFields = ["PTYPE","Label"]
        append_layer = MapUnitPolys
        append_field = labelname
        #listAppendFields = ["PTYPE","PTYPE"] #Substite this second one for the label field is present


        #Code from: https://community.esri.com/thread/185431-append-tool-and-field-mapping-help-examples
        # This is like defining an empty grid of fields you see when you run it manually in the toolbox
        fieldmappings = arcpy.FieldMappings()
        # Add the target datasets fields to the field map table
        fieldmappings.addTable(target_layer)
        # Add the append datasets fields to the field map table
        fieldmappings.addTable(append_layer)
        # At this point, you have a grid like when you run it manually saved in your field mappings.
        #####Lets map a field that have different names!
        #for i, field in enumerate(listTargetFields):



        # Find which "Index" the field has as we cant refer to them by name when editing the data only index
        field_to_map_index = fieldmappings.findFieldMapIndex(target_field)  # Field name that exists in the target layer but not append data source!
        # Grab "A copy" of the field map object for this particular field
        field_to_map = fieldmappings.getFieldMap(field_to_map_index)
        # Update its data source to add the input from the the append layer
        field_to_map.addInputField(append_layer, append_field)
        #####Lets update the master field map using this updated copy of a field
        fieldmappings.replaceFieldMap(field_to_map_index, field_to_map)
        # Create a list of append datasets and run the the tool

        arcpy.Append_management(inputs=MapUnitPolys,
                                target=gdbPath+"\\"+"GeologicMap"+"\\"+"MapUnitPolys",
                                schema_type="NO_TEST",
                                field_mapping=fieldmappings,
                                subtype="")

        arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",
                                        field="MapUnit",
                                        expression="[PTYPE]", expression_type="VB",
                                        code_block="")

        arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",
                                        field="Symbol",
                                        expression="[PTYPE]", expression_type="VB",
                                        code_block="")

        arcpy.populateMapUnitConfidence_SchemaConvert(gdbPath, "MapUnitPolys")


        #ContactsAndFaults
        arcpy.AddMessage("Adding the ContactsAndFaults")
        arcpy.Append_management(inputs=ContactsAndFaults,
                                target=gdbPath+"\\"+"GeologicMap"+"\\"+"ContactsAndFaults",
                                schema_type="NO_TEST",
                                field_mapping="",
                                subtype="")

        #arcpy.AddMessage(crosswalk)
        if crosswalk:
            arcpy.AddMessage("Doing Crosswalk")
            arcpy.AttributeByKeyValues_GEMS(gdbPath, crosswalk, True)

        #arcpy.AddMessage(datasource)
        if datasource:
            arcpy.AddMessage("Calcing DataSouceID")
            fieldname = "DataSourceID"
            arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",
                                            field=fieldname,
                                            expression="'" + datasource + "'", expression_type="PYTHON",
                                            code_block="")
            arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "ContactsAndFaults",
                                            field=fieldname,
                                            expression="'" + datasource + "'", expression_type="PYTHON",
                                            code_block="")

        arcpy.SetIDvalues2_GEMS(Input_GeMS_style_geodatabase=gdbPath, Use_GUIDs="false",
                                Do_not_reset_DataSource_IDs="true")

        #TODO make removing the tables an option
        listTablesToDelete=['DataSources','DescriptionOfMapUnits','GeoMaterialDict','Glossary']

        for table in listTablesToDelete:
            arcpy.Delete_management(gdbPath+"\\"+table)

class nbmgToGeMS(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "NBMGToGeMS"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Workspace:",
            name="workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="DB name:",
            name="dbName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="MapUnitPolys features:",
            name="polys",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Entity field name in MapUnitPolys:",
            name="polyslabelname",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="ContactsAndFaults features:",
            name="arcs",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Entity field name in ContactAndFaults:",
            name="arcslabelname",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="GEMS toolbox:",
            name="GEMS toolbox",
            datatype="Toolbox",
            parameterType="Required",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Crosswalk Table:",
            name="crosswalk table",
            datatype="DETextFile",
            parameterType="Optional",
            direction="Input")

        param8 = arcpy.Parameter(
            displayName="DataSourceID for this map:",
            name="datasource",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        params = [param0,param1,param2,param3,param4,param5,param6,param7,param8]
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
        # This is yet to be created ...

        import os

        def makefieldmapping(target_layer,listTargetFields,append_layer,listAppendFields):
            # Code adapted from: https://community.esri.com/thread/185431-append-tool-and-field-mapping-help-examples
            fieldmappings = arcpy.FieldMappings()
            fieldmappings.addTable(target_layer)
            fieldmappings.addTable(append_layer)
            for i, field in enumerate(listTargetFields):
                field_to_map_index = fieldmappings.findFieldMapIndex(listTargetFields[i])
                field_to_map = fieldmappings.getFieldMap(field_to_map_index)
                field_to_map.addInputField(append_layer, listAppendFields[i])
                fieldmappings.replaceFieldMap(field_to_map_index, field_to_map)
            return fieldmappings

        pathToWorkspace = parameters[0].valueAsText
        dbName= parameters[1].valueAsText
        MapUnitPolys = parameters[2].valueAsText
        mapunitfield =  parameters[3].valueAsText
        ContactsAndFaults = parameters[4].valueAsText
        contactsandfaultsfield = parameters[5].valueAsText
        toolbox = parameters[6].valueAsText
        toolbox2 = os.path.abspath(__file__)
        crosswalk = parameters[7].valueAsText
        datasource = parameters[8].valueAsText

        #This will only work for users on our network
        arcpy.ImportToolbox(toolbox)
        arcpy.ImportToolbox(toolbox2)
        arcpy.env.overwriteOutput = True
        # Create a new GDB
        timeDateString = datetimePrint()[0] # Gets time and date to add to export
        print(" Current Run: " + timeDateString)
        arcpy.AddMessage("Creating a GDB")

        #TODO the spatial reference frame is hardcoded
        arcpy.CreateDatabase_GEMS(Output_Workspace=pathToWorkspace,
                                  Name_of_new_geodatabase=dbName,
                                  Spatial_reference_system="PROJCS['NAD_1983_UTM_Zone_11N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-117.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
                                  Optional_feature_classes__tables__and_feature_datasets="",
                                  Number_of_cross_sections="0",
                                  Enable_edit_tracking="true",
                                  Add_fields_for_cartographic_representations="false",
                                  Add_LTYPE_and_PTTYPE="true",
                                  Add_standard_confidence_values="true")

        gdbPath=pathToWorkspace+"\\"+dbName+".gdb"

        #MapUnitPolys
        arcpy.AddMessage("Adding the MapUnitPolys")

        fieldmappings1 = makefieldmapping(gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",["PTYPE", "Label"],MapUnitPolys,[mapunitfield, mapunitfield])

        arcpy.Append_management(inputs=MapUnitPolys,
                                target=gdbPath+"\\"+"GeologicMap"+"\\"+"MapUnitPolys",
                                schema_type="NO_TEST",
                                field_mapping=fieldmappings1,
                                subtype="")

        arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",
                                        field="MapUnit",
                                        expression="[PTYPE]", expression_type="VB",
                                        code_block="")

        arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",
                                        field="Symbol",
                                        expression="[PTYPE]", expression_type="VB",
                                        code_block="")

        arcpy.populateMapUnitConfidence_SchemaConvert(gdbPath, "MapUnitPolys")


        #ContactsAndFaults
        arcpy.AddMessage("Adding the ContactsAndFaults")

        fieldmappings2 = makefieldmapping(gdbPath + "\\" + "GeologicMap" + "\\" + "ContactsAndFaults",["LTYPE"],ContactsAndFaults,[contactsandfaultsfield])

        arcpy.Append_management(inputs=ContactsAndFaults,
                                target=gdbPath+"\\"+"GeologicMap"+"\\"+"ContactsAndFaults",
                                schema_type="NO_TEST",
                                field_mapping=fieldmappings2,
                                subtype="")

        #arcpy.AddMessage(crosswalk)
        if crosswalk:
            arcpy.AddMessage("Doing Crosswalk")
            arcpy.AttributeByKeyValues_GEMS(gdbPath, crosswalk, True)

        #arcpy.AddMessage(datasource)
        if datasource:
            arcpy.AddMessage("Calcing DataSouceID")
            fieldname = "DataSourceID"
            arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "MapUnitPolys",
                                            field=fieldname,
                                            expression="'" + datasource + "'", expression_type="PYTHON",
                                            code_block="")
            arcpy.CalculateField_management(in_table=gdbPath + "\\" + "GeologicMap" + "\\" + "ContactsAndFaults",
                                            field=fieldname,
                                            expression="'" + datasource + "'", expression_type="PYTHON",
                                            code_block="")

        arcpy.SetIDvalues2_GEMS(Input_GeMS_style_geodatabase=gdbPath, Use_GUIDs="false",
                                Do_not_reset_DataSource_IDs="true")

        #TODO make removing the tables an option
        listTablesToDelete=['DataSources','DescriptionOfMapUnits','GeoMaterialDict','Glossary']

        for table in listTablesToDelete:
            arcpy.Delete_management(gdbPath+"\\"+table)