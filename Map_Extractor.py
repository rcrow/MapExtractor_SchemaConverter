import arcpy
import datetime
import pandas

#######################################################################################################################
#Some functions
def datetimePrint():
    time = datetime.datetime.now() #Get system time
    if len(str(time.month))==1:
        month="0"+str(time.month)
    else:
        month=str(time.month)
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
    return [timeDateString,date,timestr,time]

def intersectFC(FCPath,quadPath,exportPath):
    arcpy.Intersect_analysis(in_features= [FCPath, quadPath],
                             out_feature_class=exportPath,
                             join_attributes="ALL", cluster_tolerance="-1 Unknown", output_type="INPUT")

def checkAndDelete(path):
    if arcpy.Exists(path):
        print("  " + path +": Exists, Deleted")
        arcpy.Delete_management(path)
    else:
        print("  " + path +": Does Not Exist")

def NCGMPname(str,num):
    return [str[num:],str[:num]]

def clipBySelectLocation(fc):
    tempLayer = arcpy.MakeFeatureLayer_management(fc, "temp_lyr")

    arcpy.SelectLayerByLocation_management(tempLayer,
                                           'WITHIN',
                                           quad, selection_type='NEW_SELECTION',
                                           invert_spatial_relationship='INVERT')
    arcpy.DeleteFeatures_management(tempLayer)  # Delete everything outside the quad

def copyOnlyNeeded(inputfdsfullpath,exportfdsfullpath,exportfdsfullpathnew,inputprefixlength,listcorefcs):
    arcpy.env.workspace = inputfdsfullpath
    print("Workspace is: " + arcpy.env.workspace)
    listfcsInInput = arcpy.ListFeatureClasses("*")
    arcpy.env.workspace = exportfdsfullpath
    print("Workspace is: " + arcpy.env.workspace)
    for fcInInput in listfcsInInput:
        genericFileName = NCGMPname(fcInInput.split(".")[-1],inputprefixlength)[0]
        print(" ####################")
        print("     Part: "+genericFileName)
        print("     fcInInput: " + fcInInput)
        if genericFileName in listcorefcs:
            importpath = inputfdsfullpath+ "\\"+ fcInInput
            exportdestination = exportfdsfullpath + "\\" + fcInInput.split(".")[-1] #Export has initials
            print("     Import Path: " + importpath)
            print("     Check if exists: "+str(arcpy.Exists(importpath)))
            print("     Export Destintion: "+exportdestination)
            print("  Copying: " + fcInInput)
            arcpy.Copy_management(inputfdsfullpath+ "\\"+ fcInInput, exportdestination)
        else:
            print("  Skipping: " + fcInInput)
    arcpy.Rename_management(in_data=exportfdsfullpath,
                            out_data=exportfdsfullpathnew)
    print("Renaming FDS to: " + exportfdsfullpathnew)

def parsenestedlists(df,col):
    templist = map(unicode.strip, df[col].values[0].split(","))
    list = []
    for item in templist:
        nested = item.split("|")
        list.append(nested)
    print(" "+col+ ": " + str(list))
    return list

def parseValue(df,col):
    value = df[col].values[0]
    if str(value) == "nan" or str(value) == "NaN": #Is there a more graceful way to do this?
        value = ""
    print(" "+col+ " = " + str(value))
    return value

def parseList(df,col):
    value = df[col].values[0]
    if str(value) == "nan" or str(value) == "NaN":
        list = []
    else:
        list = map(unicode.strip, df[col].values[0].split(","))
    print(" "+col + ": " + str(list))
    return list

arcpy.env.overwriteOutput = True
start = datetimePrint()[3]

parametersExcelFilePath = r"extractorParametersCARR.xlsx"
#######################################################################################################################
#Import Options From Excel Sheet
toolParameters= pandas.read_excel(parametersExcelFilePath, sheet_name='ToolPaths',skiprows=1)
#print(toolParameters)
print("--------------------------------------------")
print("Toolboxes being used: ")
pathToGeMSToolB=parseValue(toolParameters,'pathToGeMSToolB')
arcpy.ImportToolbox(pathToGeMSToolB)
pathToSchemaConvertToolB = parseValue(toolParameters,'pathToSchemaConvertToolB')
arcpy.ImportToolbox(pathToSchemaConvertToolB)
pathToTableBuilderToolB = parseValue(toolParameters,'pathToTableBuilderToolB')
arcpy.ImportToolbox(pathToTableBuilderToolB)
#TODO remove hardcoding just for testing
#arcpy.ImportToolbox(r"\\Igswzcwwgsrio\loco\Team\Crow\_Python\MapExtractor\DMUTool.pyt")
#######################################################################################################################
#Import Export Details From Excel Sheet
inParameters= pandas.read_excel(parametersExcelFilePath, sheet_name='MainInputs',skiprows=1)
#print(inParameters)
print("--------------------------------------------")
print("Input parameters being used: ")
#These feature classes with be "clipped" to the quad boundary with clip
listFCsToClip = parseList(inParameters,'listFCsToClip')
#These feature classes with be "clipped" to the quad boundary using a select by location
listFCsToSelectByLocation = parseList(inParameters,'listFCsToSelectByLocation')
strlistFCsToSelectByLocation = parseValue(inParameters,'listFCsToSelectByLocation')
#Annos
listAnnos = parseList(inParameters,'listAnnos')
strlistAnnos = parseValue(inParameters,'listAnnos')

#These are the feature classes that will NOT be ignored
listCoreFCs = listFCsToClip + listFCsToSelectByLocation
listFCsToRename = listFCsToSelectByLocation + listAnnos #These are not renamed during the select by location process

inputDBPath = parseValue(inParameters,'inputDBPath')
inputFDSName= parseValue(inParameters,'inputFDSName')
inputPrefixLength = parseValue(inParameters,'inputPrefixLength') #All FCs and FDS in the import should have the same prefix (or atleast the same prefix length)
inputFDSFullPath = inputDBPath + "\\" + inputFDSName
print("FDS to be copied: "+inputFDSFullPath)
inquad = parseValue(inParameters,'inquad') #Will look for polygons with 'yes' in the 'Build' attribute

#######################################################################################################################
#Import Export Details From Excel Sheet
exParameters= pandas.read_excel(parametersExcelFilePath, sheet_name='ExportDestinations',skiprows=1)
print("--------------------------------------------")
print("Export parameters being used: ")
exportFolder = parseValue(exParameters,'exportFolder')
exportGDBPrefix = parseValue(exParameters,'exportGDBPrefix')
exportFDSPrefix = parseValue(exParameters,'exportFDSPrefix') #If this is not blank the db will not be compilant

#######################################################################################################################
#Import Options From Excel Sheet
opParameters= pandas.read_excel(parametersExcelFilePath , sheet_name='InputsOptional',skiprows=1)
print("--------------------------------------------")
print("Optional parameters being used: ")
buildPolygons = parseValue(opParameters,'buildPolygons')
removeQuad = parseValue(opParameters,'removeQuad')
removeMultiParts = parseValue(opParameters,'removeMultiParts')

makeTables = parseValue(opParameters,'makeTables')
if makeTables:
    #Input FC list and field list of lists must be in the same order
    listFCsForTables = parseList(opParameters,"listFCsForTables")
    listFieldsForTables = parsenestedlists(opParameters,"listFieldsForTables")

nullFields = parseValue(opParameters,'nullFields')
if nullFields:
    forceNull = parseValue(opParameters,'forceNull')
    listFCsToNull = parseList(opParameters,'listFCsToNull')
    #This list of lists needs to be in the same order and the above list of FCs!
    listFieldToNull = parsenestedlists(opParameters,'listFieldToNull')

dropFields = parseValue(opParameters,'dropFields')
if dropFields:
    strlistFCsToDropFldsFrom = parseValue(opParameters,'listFCsToDropFldsFrom')
    strlistFieldToDrop = parseValue(opParameters,'listFieldToDrop')
    listFCsToDropFldsFrom = parseList(opParameters,'listFCsToDropFldsFrom')
    listFieldToDrop = parsenestedlists(opParameters,'listFieldToDrop')

addExtraTable = parseValue(opParameters,'addExtraTable')
if addExtraTable:
    inputExtraTablePathGDB = parseValue(opParameters,'inputExtraTablePathGDB')
    listExtraTables = parseList(opParameters,'listExtraTables')

addCMULMU = parseValue(opParameters,'addCMULMU')
if addCMULMU:
    exportFDSCMULMU_Name = parseValue(opParameters,'exportFDSCMULMU_Name')
    inputCMULMUPathFDS = parseValue(opParameters,'inputCMULMUPathFDS')

addXSEC1 = parseValue(opParameters,'addXSEC1')
if addXSEC1:
    exportFDSXSEC1_Name = parseValue(opParameters,"exportFDSXSEC1_Name")
    inputXSECAPathFDS = parseValue(opParameters,"inputXSECAPathFDS")

addXSEC2 = parseValue(opParameters,'addXSEC2')
if addXSEC2:
    exportFDSXSEC2_Name = parseValue(opParameters,"exportFDSXSEC2_Name")
    inputXSECBPathFDS = parseValue(opParameters,"inputXSECBPathFDS")

addXSEC3 = parseValue(opParameters,'addXSEC3')
if addXSEC3:
    exportFDSXSEC3_Name = parseValue(opParameters,"exportFDSXSEC3_Name")
    inputXSECCPathFDS = parseValue(opParameters,"inputXSECCPathFDS")

addExtraFCs = parseValue(opParameters,'addExtraFCs')
if addExtraFCs:
    inputExtraFCsPathFDS = parseValue(opParameters,'inputExtraFCsPathFDS')
    listExtraFCs = parseList(opParameters,'listExtraFCs')

addDRG = parseValue(opParameters,'addDRG')
if addDRG: inputDRGRasterMosaic = parseValue(opParameters,'inputDRGRasterMosaic')

simplifyGeomorphLines = parseValue(opParameters,'simplifyGeomorphLines')
if simplifyGeomorphLines: simpSQLGeomorphLines = parseValue(opParameters,"simpSQLGeomorphLines") #Selection will be deleted

simplifyOrientationPoints = parseValue(opParameters,'simplifyOrientationPoints')
if simplifyOrientationPoints: simpSQLOrientationPoints = parseValue(opParameters,'simpSQLOrientationPoints') #Selection will be deleted

renameAllFields = parseValue(opParameters,'renameAllFields')
if renameAllFields: fieldsToRenameTable = parseValue(opParameters, 'fieldsToRenameTable')

renameSpecific = parseValue(opParameters,'renameSpecific')
if renameSpecific:
    listSpecificFCsToRename = parseList(opParameters,"listSpecificFCsToRename")
    listSpecificFieldsToRename = parsenestedlists(opParameters,"listSpecificFieldsToRename")

crossWalkFields = parseValue(opParameters,'crossWalkFields')
if crossWalkFields:
    txtFile = parseValue(opParameters,'txtFile')
    listFCsSwitchTypeAndSymbol = parseList(opParameters,'listFCsSwitchTypeAndSymbol')

crossWalkPolyAndPoints = parseValue(opParameters,'crossWalkPolyAndPoints')

changeFieldType = parseValue(opParameters,'changeFieldType')
if changeFieldType:
    listFieldsToChange = parseList(opParameters,'listFieldsToChange')
    newType = parseValue(opParameters,'newType') #All fields in listFieldToChange will be changed to this type

buildGlossary = parseValue(opParameters,'buildGlossary')
if buildGlossary:
    glossaryTable = parseValue(opParameters,'glossaryTable')
    exampleBlankGlossaryTable = parseValue(opParameters,"exampleBlankGlossaryTable")

buildDataSources = parseValue(opParameters,'buildDataSources')#This will overwrite any existing DataSources table
if buildDataSources:
    getDataSourceFromFCs = parseValue(opParameters,'getDataSourceFromFCs') #Secondary option in buildDataSources
    listFCsWithDataSourceInformation = parseList(opParameters,'listFCsWithDataSourceInformation')
    mergedTable = parseValue(opParameters,'mergedTable')
    getDataSourceFromExcel= parseValue(opParameters,'getDataSourceFromExcel') #Secondary option in buildDataSources
    extraDataSources = parseValue(opParameters,'extraDataSources')
    mergedTableAll = parseValue(opParameters,'mergedTableAll')
    #The code assumes the following is in GEMS format (build using GEMS toolbox - Create New Database)
    exampleBlankDataSourceTable = parseValue(opParameters,'exampleBlankDataSourceTable')
    dataSourceFieldNames = parseList(opParameters,'dataSourceFieldNames')
    listFCsToIgnore = parseList(opParameters,'listFCsToIgnore')

buildDMU = parseValue(opParameters,'buildDMU')
if buildDMU:
    mapUnitTable= parseValue(opParameters,'mapUnitTable')
    exampleBlankDMUTable= parseValue(opParameters,'exampleBlankDMUTable')
    nullDescription= parseValue(opParameters,'nullDescription')
    nullFillPattern= parseValue(opParameters,'nullFillPattern')
    calculateIDs= parseValue(opParameters,'calculateIDs')
    descriptionSourceID= parseValue(opParameters,'descriptionSourceID')

makeTopology = parseValue(opParameters,'makeTopology')
if makeTopology: mainLineFileName = parseValue(opParameters,'mainLineFileName') #input for makeTopology - this the final name after any renaming

calcIDNumbers = parseValue(opParameters,'calcIDNumbers')

validateDataBase = parseValue(opParameters,'validateDataBase')

populateLabelFromFeatureLinks = parseValue(opParameters,'populateLabelFromFeatureLinks')

#######################################################################################################################
#Some Naming stuff
print("--------------------------------------------")
print("Starting the core clipping functions: ")
inputCoreFDSName = inputFDSName.split(".")[-1]  # Cut off anything before the last period
inputFDSNameWOInitials = NCGMPname(inputCoreFDSName,inputPrefixLength)[0]
prefixInitials = NCGMPname(inputCoreFDSName,inputPrefixLength)[1]
print(" Prefix name: "+prefixInitials)

#######################################################################################################################
# Create a new GDB
timeDateString = datetimePrint()[0] # Gets time and date to add to export
print(" Current Run: " + timeDateString)

#Export names and proj
exportGDBName = exportGDBPrefix + timeDateString
spatialRef = arcpy.Describe(inputFDSFullPath).spatialReference

exportGDBFullPath = exportFolder + "\\" + exportGDBName + ".gdb"
print(" Creating a new GDB at: "+exportGDBFullPath)
arcpy.CreateFileGDB_management(out_folder_path=exportFolder,
                               out_name=exportGDBName,
                               out_version="CURRENT")
#Create a FDS
arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                      out_name=inputCoreFDSName,
                                      spatial_reference=spatialRef)

exportFDSFullPath = exportGDBFullPath + "\\" + inputCoreFDSName
print(" Created a new FDS at: "+exportFDSFullPath)

exportFDSFullPathNew = exportGDBFullPath + "\\" + exportFDSPrefix + inputFDSNameWOInitials

print(" Starting to copy everything over...")
copyOnlyNeeded(inputFDSFullPath,
               exportFDSFullPath,
               exportFDSFullPathNew,
               inputPrefixLength,
               listCoreFCs)

#######################################################################################################################
#Get the quads of interest from the FOCUS area feature class
# Only use quads that are labeled as active
quad = exportFDSFullPathNew + "\\" + "selectedQuad"
quadTemp = exportFDSFullPathNew + "\\" + "TempQuad"
print(" Finding active boundaries...")
arcpy.Select_analysis(inquad,
                      quadTemp,
                      "Build = 'yes'")
arcpy.Union_analysis(in_features=quadTemp,
                     out_feature_class=quad,
                     join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
arcpy.DeleteIdentical_management(in_dataset=quad,
                                 fields="Shape",
                                 xy_tolerance="",
                                 z_tolerance="0")
#TODO do check here to make sure that a polygon ended up in quad
checkAndDelete(quadTemp)

#######################################################################################################################
#Copy the db
arcpy.Copy_management(quad,
                      exportFDSFullPathNew+"\\"+"QuadBoundary")

#######################################################################################################################
#Make lists of stuff
arcpy.env.workspace = exportFDSFullPathNew
listFCsInExportDB = arcpy.ListFeatureClasses("*", "All")
listLength = len(listFCsInExportDB)
print(listFCsInExportDB)
listFCsInExportDB.remove("selectedQuad") #Don't clip the quad with the quad

#######################################################################################################################
#Clipping Everything
print("Clipping the FCs...")
# Cycle through all the feature classes
for fcInExportDB in listFCsInExportDB:
    fcPath = arcpy.env.workspace + "\\" + fcInExportDB  # Get the full path
    print(" ####################")
    print("    Feature class full path: " + fcPath)
    fcName = NCGMPname(fcInExportDB,inputPrefixLength)[0] #Truncates initial at start of name
    print("    Feature class name: " + fcName)
    if fcName == "ContactsAndFaults":
        fcExportPath = exportFDSFullPathNew+"\\"+fcName+"_temp" #ContactsAndFaults temp till quad added
    else:
        fcExportPath = exportFDSFullPathNew + "\\" + fcName
    if fcName in listFCsToClip: #if in clip array
        print("    Using Clip")
        arcpy.Clip_analysis(
            in_features=fcPath,
            clip_features=quad,
            out_feature_class=fcExportPath, #if you export this to the same FDS the feature links seem to be preserved
            cluster_tolerance="")
        print("  Finished clipping: " + fcName)
        if fcName == "ContactsAndFaults":
            # Add quad and build polygons REQUIRES CONTACTS AND FAULTS
            quadLine = exportFDSFullPathNew + "\\" + "quadLines"
            # Convert the polys to lines
            arcpy.FeatureToLine_management(quad, quadLine)
            # This will change the type of everything in the FC to 31.08
            with arcpy.da.UpdateCursor(quadLine, ["Type"]) as cursor:
                for row in cursor:
                    row[0] = '31.08' #Map neatline
                    cursor.updateRow(row)
            arcpy.Merge_management([fcExportPath, quadLine],
                                   exportFDSFullPathNew + "\\" + "ContactsAndFaults_temp2")
            if removeMultiParts:
                arcpy.MultipartToSinglepart_management(
                    in_features=exportFDSFullPathNew + "\\" + "ContactsAndFaults_temp2",
                    out_feature_class=exportFDSFullPathNew + "\\" + "ContactsAndFaults")
            else:
                arcpy.CopyFeatures_management(exportFDSFullPathNew + "\\" + "ContactsAndFaults_temp2",
                                              exportFDSFullPathNew + "\\" + "ContactsAndFaults")
            checkAndDelete(exportFDSFullPathNew + "\\" + "ContactsAndFaults_temp2")
            checkAndDelete(fcExportPath)  # Bcz temp name
        checkAndDelete(fcPath)
    elif fcName in listFCsToSelectByLocation:
        print("    Doing a select by location")
        clipBySelectLocation(exportFDSFullPathNew + "\\" + prefixInitials + fcName)
    else:
        print("    Ignoring: " + fcName)

#######################################################################################################################
#rename the feature classes with feature linked anno
print(listFCsToRename)
for fcToRename in listFCsToRename:
    print ("Renaming: " + fcToRename)
    arcpy.Rename_management(in_data=exportFDSFullPathNew + "\\" + prefixInitials + fcToRename,
                              out_data=exportFDSFullPathNew + "\\" + fcToRename)

#######################################################################################################################
#OPTIONS
print("--------------------------------------------")
if addCMULMU:
    print("Adding CMU / LMU...")
    arcpy.Copy_management(inputCMULMUPathFDS, exportGDBFullPath + "\\" + exportFDSCMULMU_Name)

if addXSEC1:
    print("Adding CrossSection A")
    arcpy.Copy_management(inputXSECAPathFDS, exportGDBFullPath + "\\" + exportFDSXSEC1_Name)

if addXSEC2:
    print("Adding CrossSection B")
    arcpy.Copy_management(inputXSECBPathFDS, exportGDBFullPath + "\\" + exportFDSXSEC2_Name)

if addXSEC3:
    print("Adding CrossSection C")
    arcpy.Copy_management(inputXSECCPathFDS, exportGDBFullPath + "\\" + exportFDSXSEC3_Name)

if addExtraFCs:
    print("Adding extra FCs...")
    for extraFC in listExtraFCs:
        arcpy.Copy_management(inputExtraFCsPathFDS + "\\" + extraFC, exportFDSFullPathNew + "\\" + extraFC)

usePopulateLabelTool = False
if populateLabelFromFeatureLinks:
    if usePopulateLabelTool:
        #TODO get this working through the toolbox
        arcpy.populateLabelFromFeatureLinks_SchemaConvert(
            gdb=exportGDBName,
            fds=exportFDSFullPathNew,
            annos=strlistAnnos, fcs=strlistFCsToSelectByLocation, nullFirst='true')
    else:
        print("Populating the Label field from the feature-linked annotations...")
        arcpy.env.workspace = exportGDBFullPath
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(False, True)
        edit.startOperation()
        for i, anno in enumerate(listAnnos):
            annoPath = exportFDSFullPathNew + "\\" + anno
            with arcpy.da.SearchCursor(annoPath,
                                       ["featureid", "textstring"]) as cursor:  # Note lowercase names from postgres
                listFeatureIds = []
                listLabels = []
                for row in cursor:
                    listFeatureIds.append(row[0])
                    listLabels.append(row[1])
            fcPath = exportFDSFullPathNew + "\\" + listFCsToSelectByLocation[i]
            arcpy.CalculateField_management(fcPath, "label", "NULL")
            with arcpy.da.UpdateCursor(fcPath, ["objectid", "label"]) as editcursor:
                for editrow in editcursor:
                    if editrow[0] in listFeatureIds:
                        index = listFeatureIds.index(editrow[0])
                        editrow[1] = listLabels[index]
                        editcursor.updateRow(editrow)
        edit.stopOperation()
        edit.stopEditing(True)

if calcIDNumbers:
    print("Adding ID fields...")
    #Make sure the FCs have the needed fields
    arcpy.env.workspace = exportGDBFullPath
    listFDSInGDB = arcpy.ListDatasets()
    for finalfds in listFDSInGDB:  # this goes through all the FDS is that needed?
        listFCsinFinalFDS = arcpy.ListFeatureClasses(feature_dataset=finalfds)
        for finalfc in listFCsinFinalFDS:
            fcpath = exportGDBFullPath + "\\" + finalfds + "\\" + finalfc
            print(" Feature Class: " + finalfc)
            fieldsInFC = arcpy.ListFields(fcpath)
            fieldNamesinFC = [x.name for x in fieldsInFC]
            # print(fieldNamesinFC)
            if finalfc + "_ID" in fieldNamesinFC:
                print("  The ID field is already present in: " + finalfc)
            else:
                print("  Adding the ID field to: " + finalfc)
                arcpy.AddField_management(in_table=fcpath,
                                          field_name=finalfc + "_ID",
                                          field_type="TEXT",
                                          field_length=50)
    print("Calcing ID fields...")
    arcpy.SetIDvalues2_GEMS(Input_GeMS_style_geodatabase=exportGDBFullPath,Use_GUIDs="false", Do_not_reset_DataSource_IDs="true")


if buildPolygons:
    print("Building polygons...")
    #Build polygons lines MUST be labeled ContactsAndFault and points MapUnitPoints
    print("  Populating symbol in MapUnit Points...")
    arcpy.CalculateField_management(in_table=exportFDSFullPathNew+"\\"+'MapUnitPoints',
                                    field='symbol',
                                    expression='[mapunit]',
                                    expression_type='VB',
                                    code_block="")
    arcpy.FeatureToPolygon_management(in_features=exportFDSFullPathNew+"\\"+'ContactsAndFaults',
                                          out_feature_class=exportFDSFullPathNew+"\\"+'MapUnitPolys',
                                          cluster_tolerance="#",
                                          attributes="ATTRIBUTES",
                                          label_features=exportFDSFullPathNew+"\\"+'MapUnitPoints')
    arcpy.AddField_management(in_table=exportFDSFullPathNew+"\\"+'MapUnitPolys',
                              field_name="MapUnitPolys_ID",
                              field_type="TEXT",
                              field_length=50)
    print("  Populating symbol in MapUnit Polys...")
    arcpy.CalculateField_management(in_table=exportFDSFullPathNew+"\\"+'MapUnitPolys',
                                    field='symbol',
                                    expression='[mapunit]',
                                    expression_type='VB',
                                    code_block="")

if simplifyGeomorphLines:
    print("Simplifying the geomorph lines...")
    #delete all lines except lineaments from GeomorphLines
    fcName="GeomorphLines"
    tempLayer = arcpy.MakeFeatureLayer_management(exportFDSFullPathNew + "\\" + fcName,"GMorph_lyr")
    arcpy.SelectLayerByAttribute_management(tempLayer,"NEW_SELECTION",simpSQLGeomorphLines)
    arcpy.DeleteFeatures_management(tempLayer)

if simplifyOrientationPoints:
    print("Simplifying the orientation points...")
    fcName = "OrientationPoints"
    tempLayer = arcpy.MakeFeatureLayer_management(exportFDSFullPathNew + "\\" + fcName,"Orient_lyr")
    arcpy.SelectLayerByAttribute_management(tempLayer,"NEW_SELECTION",simpSQLOrientationPoints)
    arcpy.DeleteFeatures_management(tempLayer)

if makeTables:
    print("Making frequency tables ...")
    for i, fcForTable in enumerate(listFCsForTables):
        fullPathFC = exportFDSFullPathNew + "\\" + fcForTable
        #print(fullPathFC)
        for field in listFieldsForTables[i]:
            #print(field)
            fullPathTable = exportGDBFullPath + "\\" + fcForTable + "_" + field
            arcpy.Frequency_analysis(fullPathFC,
                                     fullPathTable,
                                     field)

useDropTool=False
if dropFields:
    if useDropTool:
        arcpy.dropFieldsFromSpecific_SchemaConvert(listFCsToDropFldsFrom=strlistFCsToDropFldsFrom,
                                                   listFieldsToDrop=strlistFieldToDrop,
                                                   gdb=exportGDBFullPath)
    else:
        for x, fctodrop in enumerate(listFCsToDropFldsFrom):
            #print(fctodrop)
            fcFullPath = exportFDSFullPathNew + "\\" + fctodrop
            # Note if you use different disable tracking field the following will have to be changes
            arcpy.DisableEditorTracking_management(fcFullPath, "DISABLE_CREATOR", "DISABLE_CREATION_DATE",
                                                   "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
            listfields=arcpy.ListFields(fcFullPath, listFieldToDrop[x])
            if len(listfields) > 0:
                print("  Removing fields from: " + fctodrop )
                arcpy.DeleteField_management(fcFullPath, listFieldToDrop[x])

if nullFields:
    print("Nulling out fields...")
    for s, fctonull in enumerate(listFCsToNull):
        print(" Feature class to null: " + fctonull)
        fcFullPathN = exportFDSFullPathNew + "\\" + fctonull #TODO this will only go through the newly extracted FDS, consider
        #print("  " + fcFullPathN)
        for fieldname in listFieldToNull[s]:
            if len(arcpy.ListFields(fctonull, fieldname)) > 0:  # Make sure the field exists
                field = arcpy.ListFields(fctonull, fieldname)
                cannull = field[0].isNullable
                if cannull:
                    print("  Nulling: " + fieldname)
                    arcpy.CalculateField_management(fctonull, fieldname, "NULL")
                else:
                    if forceNull:
                        print(" Forcing Null...")
                        fieldtype = field[0].type
                        fieldlength = field[0].length
                        fieldDomain = field[0].domain
                        print("   Field type is: " + fieldtype)
                        print("   Field length is: " + str(fieldlength))
                        if len(fieldDomain) > 0:
                            print("   Field domain is: " + fieldDomain)
                            print("   Can't null a field with an attached domain")
                        else:
                            print("   No domain is attached")
                            if fieldtype == "Double" or fieldtype == "Integer" or fieldtype == "Single" or fieldtype == "SmallInteger":
                                print("    Calcing to -9999...")
                                arcpy.CalculateField_management(in_table=fctonull,
                                                                field=fieldname,
                                                                expression="-9999",
                                                                expression_type="VB",
                                                                code_block="")
                            elif fieldtype == "String" and fieldlength > 4:
                                print("    Calcing to #null...")
                                arcpy.CalculateField_management(in_table=fctonull,
                                                                field=fieldname,
                                                                expression=fieldname + " = " + "\"#null\"",
                                                                expression_type="VB",
                                                                code_block="")

                            elif fieldtype == "String" and fieldlength < 4:
                                print("    Calcing to #...")
                                arcpy.CalculateField_management(in_table=fctonull,
                                                                field=fieldname,
                                                                expression=fieldname + " = " + "\"#\"",
                                                                expression_type="VB",
                                                                code_block="")
                            else:
                                print("Field type: " + fieldtype + " not recognized")
            else:
                print("Field name: " + fieldname + " does not exist")

if addExtraTable:
    print("Adding extra tables...")
    for extraTable in listExtraTables:
        arcpy.Copy_management(inputExtraTablePathGDB + "\\" + extraTable, exportGDBFullPath + "\\" + extraTable)
        print ("  Copying " + extraTable)

if addDRG:
    print("Adding the DRG...")
    arcpy.env.workspace = exportGDBFullPath
    arcpy.Clip_management(in_raster=inputDRGRasterMosaic,
                          out_raster="DRG",
                          in_template_dataset=quad, nodata_value="256",
                          clipping_geometry="ClippingGeometry", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

if removeQuad:
    print("Removing the quad...")
    arcpy.env.workspace = exportFDSFullPathNew
    checkAndDelete(quadLine)
    checkAndDelete(quad)
    checkAndDelete(exportFDSFullPathNew+"\\"+"QuadBoundary")

if renameAllFields:
    print("Renaming fields...")
    dfRename = pandas.read_excel(fieldsToRenameTable)
    sdeFieldNames = dfRename['sdeField'].values.tolist()
    gemsFieldNames = dfRename['GEMSField'].values.tolist()
    arcpy.env.workspace = exportGDBFullPath
    listFDSInGDB = arcpy.ListDatasets()
    for finalfds in listFDSInGDB: #this goes through all the FDS is that needed?
        listFCsinFinalFDS = arcpy.ListFeatureClasses(feature_dataset=finalfds)
        for finalfc in listFCsinFinalFDS:
            fcpath = exportGDBFullPath + "\\" + finalfds + "\\" + finalfc
            print("   Feature Class for field renaming: " + finalfc)
            fieldsToRename = arcpy.ListFields(fcpath)
            for numb, field in enumerate(fieldsToRename):  # TODO no nead to enumerate
                #print(field.name)
                if field.name in sdeFieldNames:
                    newfieldname = gemsFieldNames[sdeFieldNames.index(field.name)]
                    arcpy.AlterField_management(fcpath, field.name,"zzzz")  # Without this simple case changes are not always recognized
                    arcpy.AlterField_management(fcpath, "zzzz", newfieldname)
                    print("     -" + field.name + " renamed to: " + newfieldname)
                else:
                    print("      Did not need to rename: " + field.name)
            if renameSpecific and finalfc in listSpecificFCsToRename:
                print("     Renaming Field in Specific FC...")
                #print(listSpecificFieldsToRename)
                renameIdx = listSpecificFCsToRename.index(finalfc)
                #print(renameIdx)
                oldName = listSpecificFieldsToRename[renameIdx][0]
                newName = listSpecificFieldsToRename[renameIdx][1]
                print("       Old name: "+oldName + " New name: " + newName)
                arcpy.AlterField_management(fcpath, oldName, newName)

if crossWalkFields:
    print("Crosswalking fields...")
    for finalfds2 in listFDSInGDB:
        listFCsinFinalFDS2 = arcpy.ListFeatureClasses(feature_dataset=finalfds2)
        for finalfc2 in listFCsinFinalFDS2:
            fcpath2 = exportGDBFullPath + "\\" + finalfds2 + "\\" + finalfc2
            #print(finalfc2)
            if finalfc2 in listFCsSwitchTypeAndSymbol:
                print(" Switching Type to Symbol for: " +finalfc2)
                arcpy.CalculateField_management(fcpath2, "Symbol", "[Type]")
    #Note: AttributeByKeyValues fails when other FCs are in the text file
    arcpy.AttributeByKeyValues_GEMS(exportGDBFullPath, txtFile, True)

if changeFieldType:
    print("Changing field types...")
    arcpy.env.workspace = exportGDBFullPath
    listFDSInGDB = arcpy.ListDatasets()
    for finalfds in listFDSInGDB:  # this goes through all the FDS is that needed?
        listFCsinFinalFDS = arcpy.ListFeatureClasses(feature_dataset=finalfds)
        print("  Looking in FDS: " + str(finalfds))
        for finalfc in listFCsinFinalFDS:
            fcpath = exportGDBFullPath +"\\" + finalfds + "\\" + finalfc
            listfieldsfortypechange = arcpy.ListFields(fcpath)
            print("    Looking in FC: " + str(finalfc))
            for fieldtype in listfieldsfortypechange:
                if fieldtype.name in listFieldsToChange:
                    print("     -" + fieldtype.name + " type changing to: " + newType)
                    arcpy.AddField_management(fcpath, "temp", newType)
                    #print(fieldtype.name)
                    arcpy.env.workspace = exportGDBFullPath
                    edit = arcpy.da.Editor(arcpy.env.workspace)
                    edit.startEditing(False, True)
                    edit.startOperation()
                    arcpy.CalculateField_management(fcpath, "temp", "!"+fieldtype.name+"!","PYTHON")
                    edit.stopOperation()
                    edit.stopEditing(True)
                    arcpy.DeleteField_management(fcpath, fieldtype.name)
                    arcpy.AlterField_management(fcpath, "temp", fieldtype.name)

if crossWalkPolyAndPoints:
    print("Crosswalking polys and points...")
    for finalfds3 in listFDSInGDB:
        listFCsinFinalFDS3 = arcpy.ListFeatureClasses(feature_dataset=finalfds3)
        for finalfc3 in listFCsinFinalFDS3:
            fcpath3 = exportGDBFullPath + "\\" + finalfds3 + "\\" + finalfc3
            #print(finalfc3)
            #print(fcpath3)
            if finalfc3 in ["MapUnitPoints", "MapUnitPolys"]:
                arcpy.env.workspace = exportGDBFullPath
                #print(arcpy.env.workspace)
                edit = arcpy.da.Editor(arcpy.env.workspace)
                edit.startEditing(False, True)
                edit.startOperation()
                with arcpy.da.UpdateCursor(fcpath3, ['MapUnit', 'IdentityConfidence']) as cursor3:
                    for row3 in cursor3:
                        if str(row3[0]).find("?") == -1:
                            row3[1] = "certain"
                        else:
                            row3[1] = "questionable"
                        cursor3.updateRow(row3)
                edit.stopOperation()
                edit.stopEditing(True)

if buildGlossary:
    arcpy.buildGlossary_TableBuilder(
        glossaryTable=glossaryTable,
        gdb=exportGDBFullPath,
        exampleBlankGlossaryTable=exampleBlankGlossaryTable,
        onlyTables="")

if buildDataSources:
    print("Building DataSources table...")
    arcpy.env.overwriteOutput = True
    # Merge all the footprints to get a master list of datasources
    mergedFCs = r"in_memory\mergedFCs"
    arcpy.Merge_management(listFCsWithDataSourceInformation, mergedFCs)
    arcpy.TableToExcel_conversion(Input_Table=mergedFCs,
                                  Output_Excel_File=mergedTable)
    arcpy.Delete_management(mergedFCs)

    master_DataSourceID = []
    master_Authors = []
    master_URL = []
    master_Reference = []

    if getDataSourceFromFCs:
        df = pandas.read_excel(mergedTable)
        master_DataSourceID = master_DataSourceID + df['FOLDERNAME'].values.tolist()
        master_Authors = master_Authors + df['AUTHORS'].values.tolist()
        master_URL = master_URL + df['SOURCEURL'].values.tolist()
        master_Reference = master_Reference = df['REFERENCE'].values.tolist()

    if getDataSourceFromExcel:
        # Add extra DataSources
        df2 = pandas.read_excel(extraDataSources)
        # print(df2)
        master_DataSourceID = master_DataSourceID + df2['FOLDERNAME'].values.tolist()
        master_Authors = master_Authors + df2['AUTHORS'].values.tolist()
        master_URL = master_URL + df2['SOURCEURL'].values.tolist()
        master_Reference = master_Reference + df2['REFERENCE'].values.tolist()

    if getDataSourceFromExcel and getDataSourceFromFCs:
        writer = pandas.ExcelWriter(mergedTableAll)
        headerDS = pandas.DataFrame(["FOLDERNAME","AUTHORS","SOURCEURL","REFERENCE"]).T
        headerDS.to_excel(writer,'Sheet1',header=False,index=False)
        pandas.DataFrame([master_DataSourceID]).T.to_excel(writer, 'Sheet1', header=False, index=False,startrow=1,startcol=0)
        pandas.DataFrame([master_Authors]).T.to_excel(writer, 'Sheet1', header=False, index=False,startrow=1,startcol=1)
        pandas.DataFrame([master_URL]).T.to_excel(writer, 'Sheet1', header=False, index=False,startrow=1, startcol=2)
        pandas.DataFrame([master_Reference]).T.to_excel(writer, 'Sheet1', header=False, index=False,startrow=1,startcol=3)
        writer.save()

    arcpy.buildDataSources_TableBuilder(
        masterDataSourcesTable=mergedTableAll,
        gdb=exportGDBFullPath,
        exampleBlankDataSourceTable=exampleBlankDataSourceTable,
        onlyTables="")

useStandAloneTool = False
if buildDMU:
    if useStandAloneTool:
        if nullDescription:
            nullDescription = 'true'
        else:
            nullDescription = ''
        arcpy.AddMessage("Null description: " + nullDescription)

        if nullFillPattern:
            nullFillPattern = 'true'
        else:
            nullFillPattern = ''
        arcpy.AddMessage("Null fill pattern: " + nullFillPattern)

        if calcIDNumbers:
            calcIDNumbers = 'true'
        else:
            calcIDNumbers = ''
        arcpy.AddMessage("calcIDNumbers: " + calcIDNumbers)

        arcpy.AddMessage("Loading DMU tool")
        arcpy.AddMessage("Using the SchemaConvert version")
        arcpy.buildDMUFramework_TableBuilder(MasterMapUnitTable=mapUnitTable,
                                              gdb=exportGDBFullPath,
                                              exampleBlankDMUTable=exampleBlankDMUTable,
                                              NullDescription=nullDescription,
                                              NullPattern=nullFillPattern,
                                              calcIDs=calcIDNumbers,
                                              descSourceID=descriptionSourceID)

    else:
        arcpy.env.overwriteOutput = True
        arcpy.AddMessage("Building DMU table with out the tool...")
        dfG = pandas.read_excel(mapUnitTable)
        headerDMU = list(dfG.columns.values)

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

        arcpy.env.workspace = exportGDBFullPath
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

        DMUTablePath = exportGDBFullPath + "\\" + "DescriptionOfMapUnits"
        arcpy.Copy_management(exampleBlankDMUTable, DMUTablePath)
        # arcpy.DeleteRows_management(gdb + "\\" + "Glossary")  # Empty the table
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
        # arcpy.AddField_management(gdb + "\\" + "DescriptionOfMapUnits","TempOrder","Integer")
        cursor = arcpy.da.InsertCursor(DMUTablePath,
                                       ['MapUnit', 'Name', 'Age', 'Description', 'FullName', 'HierarchyKey',
                                        'ParagraphStyle', 'Label',
                                        'Symbol', 'AreaFillRGB', 'AreaFillPatternDescription', 'GeoMaterial',
                                        'GeoMaterialConfidence'])
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

        if calculateIDs:
            arcpy.AddMessage("Calculating DescriptionOfMapUnits IDs...")
            arcpy.CalculateField_management(DMUTablePath, 'DescriptionOfMapUnits_ID', "\"DMU\"&[OBJECTID]")

        if isinstance(descriptionSourceID, unicode):
            arcpy.AddMessage("Assigning Source IDs...")
            arcpy.CalculateField_management(DMUTablePath, 'DescriptionSourceID', "\"" + descriptionSourceID + "\"")

        arcpy.env.overwriteOutput = False


if buildGlossary:
    #Go through the newly created tables now
    print("Building Glossary table from tables...")
    arcpy.buildGlossary_TableBuilder(
        glossaryTable=glossaryTable,
        gdb=exportGDBFullPath,
        exampleBlankGlossaryTable="",
        onlyTables="true")

if buildDataSources:
    #No Glossary term in DataSources table so run this last
    #Go through the newly created tables now
    print("Building DataSources table from tables...")
    arcpy.buildDataSources_TableBuilder(
        masterDataSourcesTable=mergedTableAll,
        gdb=exportGDBFullPath,
        exampleBlankDataSourceTable="",
        onlyTables="true")

if makeTopology:
    print("Making topology...")
    TopologyName = 'GeologicMap_Topology'
    Topology = exportFDSFullPathNew + "\\" + TopologyName
    arcpy.CreateTopology_management(exportFDSFullPathNew, TopologyName, in_cluster_tolerance="")
    fileNameCF = exportFDSFullPathNew + "\\" + mainLineFileName
    arcpy.AddFeatureClassToTopology_management(Topology, fileNameCF, xy_rank="1", z_rank="1")
    arcpy.AddRuleToTopology_management(Topology, rule_type="Must Not Overlap (Line)",
                                       in_featureclass=fileNameCF, subtype="", in_featureclass2="#", subtype2="")
    arcpy.AddRuleToTopology_management(Topology, rule_type="Must Not Have Dangles (Line)",
                                       in_featureclass=fileNameCF, subtype="", in_featureclass2="#", subtype2="")
    arcpy.AddRuleToTopology_management(Topology, rule_type="Must Be Single Part (Line)",
                                       in_featureclass=fileNameCF, subtype="", in_featureclass2="#", subtype2="")
    arcpy.AddRuleToTopology_management(Topology, rule_type="Must Not Intersect Or Touch Interior (Line)",
                                       in_featureclass=fileNameCF, subtype="", in_featureclass2="#", subtype2="")
    arcpy.AddRuleToTopology_management(Topology, rule_type="Must Not Have Pseudo-Nodes (Line)",
                                       in_featureclass=fileNameCF, subtype="", in_featureclass2="#", subtype2="")
    arcpy.AddRuleToTopology_management(Topology, rule_type="Must Not Self-Intersect (Line)",
                                       in_featureclass=fileNameCF, subtype="", in_featureclass2="#", subtype2="")
    arcpy.ValidateTopology_management(Topology)
    print("Topology done")

if calcIDNumbers:
    print("Calcing ID fields...")
    arcpy.SetIDvalues2_GEMS(Input_GeMS_style_geodatabase=exportGDBFullPath,Use_GUIDs="false", Do_not_reset_DataSource_IDs="true")

if validateDataBase:
    print("Validating the database...")
    arcpy.ValidateDatabase_GEMS(
        Input_geodatabase=exportGDBFullPath,
        Output_workspace="")

end = datetimePrint()[3]
elapsed = end-start
print("Elapsed time: "+str(elapsed))

arcpy.env.overwriteOutput = False


