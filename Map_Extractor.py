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

arcpy.env.overwriteOutput = True

#######################################################################################################################
#Input lists
#These feature classes with be "clipped" to the quad boundary with clip
listFCsToClip = ['ContactsAndFaults']
#These feature classes with be "clipped" to the quad boundary using a select by location
listFCsToSelectByLocation = ['MapUnitPoints']
#Annos
listAnnos = ['MapUnitPointsAnno24k']

#These are the feature classes that will NOT be ignored
listCoreFCs = listFCsToClip + listFCsToSelectByLocation
listFCsToRename = listFCsToSelectByLocation + listAnnos #These are not renamed during the select by location process

#######################################################################################################################
#Export destinations
exportFolder = r"\\igswzcwwgsrio\loco\Team\Crow\_TestingSandbox\MapExtractor"
exportGDBPrefix = "Test_"
exportFDSPrefix = "" #If this is not blank the db will not be compilant

#######################################################################################################################
#Options
buildPolygons = True
removeQuad = True
removeMultiParts = True

makeTables = False
#Input FC list and field list of lists must be in the same order
listFCsForTables = ["ContactsAndFaults",
                    "MapUnitPoints",
                    "MapUnitPolys"]
listFieldsForTables = [['type'],
                       ['mapunit'],
                       ['mapunit']]
#print("Length of FieldsForTables : " +str(len(listFieldsForTables)))

nullFields = True
forceNull = False #Tries to use other representations like #null, #, or -9999 if field is not nullable
listFCsToNull = ['ContactsAndFaults',#2
                         'MapUnitPoints',#3
                         'MapUnitPolys']#6
#This list of lists needs to be in the same order and the above list of FCs!
listFieldToNull = [["symbol","label","notes"],
                   ["symbol","label","notes"],
                   ["symbol","label","notes"]]

dropFields = True
listFCsToDropFldsFrom = ['ContactsAndFaults',#2
                         'MapUnitPoints',#3
                         'MapUnitPolys']#6
#This list of lists needs to be in the same order and the above list of FCs!
listFieldToDrop = [['creator','createdate','editor','editdate','datasourcenotes',
                         'checkby','checknotes','validsmall','FID_selectedQuad','FID_TempQuad','Name','Active','Build','ORIG_FID'],#2
                   ['mapunit2','origunit','creator',
                         'createdate','editor','editdate','datasourcenotes','facies','checkby','checknotes','validsmall'],#3
                   ['mapunit2','origunit','creator',
                         'createdate','editor','editdate','datasourcenotes','facies','checkby','checknotes','validsmall'],#4
                   ]

addExtraTable = True
inputExtraTablePathGDB = r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSReferenceGBDs\SimpleGDB.gdb"
listExtraTables = ['GeoMaterialDict','DescriptionOfMapUnits']

addCMULMU = False
exportFDSCMULMU_Name = "CorrelationOfMapUnits"
inputCMULMUPathFDS = r"Database Connections\Connection to igswzcwggsmoki.wr.usgs.gov_LOCOMAPS_RCROW.sde\locomaps.dbo.SMSECorrelationOfMapUnits"

addXSEC1 = False
exportFDSXSEC1_Name = "CrossSectionA"
inputXSECAPathFDS = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\SMSE_Xsec.gdb\XSectionA"

addXSEC2 = False
exportFDSXSEC2_Name = "CrossSectionB"
inputXSECBPathFDS = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\SMSE_Xsec.gdb\XSectionB"

addXSEC3 = False
exportFDSXSEC3_Name = "CrossSectionC"
inputXSECCPathFDS = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\SMSE_Xsec.gdb\XSectionC"

addExtraFCs = False
inputExtraFCsPathFDS = r"\\Igswzcwwgsrio\loco\Team\Felger\ActiveMaps\CastleRock24k_USGS\GIS\CR24k_PostPubsReview\CR24k_Extract_20180809\CastleRock24k_20180809_1254_06.gdb"
listExtraFCs = ['DataSourcePolys','GenericSamples','GenericSamplesAnno','MiscAnno']

addDRG = False
inputDRGRasterMosaic = r"\\igswzcwwgsrio\DataLibrary\GMEG_DataLibraryLinks\TOPOMAPS_DRG24K_AZ.lyr"

simplifyGeomorphLines = False
simpSQLGeomorphLines = " NOT type = '04.01.01' " #Selection will be deleted

simplifyOrientationPoints = False
simpSQLOrientationPoints = " NOT plotatscale = 24000 " #Selection will be deleted

renameAllFields = True
fieldsToRenameTable = r"\\igswzcwwgsrio\loco\Team\Crow\_TestingSandbox\MrMerger\fieldsCapTable.xlsx"

crossWalkFields = True
txtFile = r"\\Igswzcwwgsrio\loco\Team\Crow\_TestingSandbox\MapExtractor\ContactsAndFaults_Crosswalk.txt"
listFCsSwitchTypeAndSymbol = ["ContactsAndFaults"]

crossWalkPolyAndPoints = True

buildGlossary = True
glossaryTable = r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSConversionFiles\TypeAndDefsForConversion.xls"
exampleBlankGlossaryTable = r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSReferenceGBDs\SimpleGDB.gdb\Glossary"

buildDataSources = True #This will overwrite any existing DataSources table
getDataSourceFromFCs=True #Secondary option in buildDataSources
miscMaps = r"\\IGSWZCWWGSRIO\DataLibrary\GeologyData\GeologicMaps\ReferenceData\GeologicMaps.gdb\GeologicMapBoundaries\MiscellaneousMaps"
quadMaps = r"\\IGSWZCWWGSRIO\DataLibrary\GeologyData\GeologicMaps\ReferenceData\GeologicMaps.gdb\GeologicMapBoundaries\QuadMaps"
stateMaps = r"\\IGSWZCWWGSRIO\DataLibrary\GeologyData\GeologicMaps\ReferenceData\GeologicMaps.gdb\GeologicMapBoundaries\StateMaps"
thesisMaps = r"\\IGSWZCWWGSRIO\DataLibrary\GeologyData\GeologicMaps\ReferenceData\GeologicMaps.gdb\GeologicMapBoundaries\ThesisMaps"
getDataSourceFromExcel=True #Secondary option in buildDataSources
extraDataSources = r"\\igswzcwwgsrio\loco\Team\Felger\TEMP\4DataLibrary\MapFootprints_Table_Temp.xls"
#The code assumes the following is in GEMS format (build using GEMS toolbox - Create New Database)
exampleBlankDataSourceTable = r"\\Igswzcwwgsrio\loco\Geology\SDE_Stuff\GEMSReferenceGBDs\SimpleGDB.gdb\DataSources"
dataSourceFieldNames = ["DataSourceID","LocationSourceID","AnalysisSourceID","OrientationSourceID","DefinitionSourceID"]
listFCsToIgnore = ["AllPolys_Merge20180924","BouseheadPts","BousePts","BullheadPts","ChemehueviPts","PaloVerdePts"]
mergedTable = r"\\igswzcwwgsrio\loco\Geology\SDE_Stuff\DataSourceTables\MergedMapFootprints_Table.xls"

makeTopology = True
mainLineFileName = "ContactsAndFaults" #input for makeTopology - this the final name after any renaming

calcIDNumbers = True

validateDataBase = True

#######################################################################################################################
#Input files
inputDBPath = r"\\Igswzcwwgsrio\loco\Team\Crow\_TestingSandbox\MapExtractor\RSCgeoKiva_20181104_0813_29_RSC_copy.gdb"
inputFDSName="RSCGeologicMap"
inputPrefixLength = 3 #All FCs and FDS in the import should have the same prefix (or atleast the same prefix length)
inputFDSFullPath = inputDBPath + "\\" + inputFDSName
print("FDS to be copied: "+inputFDSFullPath)
inquad = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\LOCOBigBrother\LOCOBigBrother.gdb\Focus_RSC" #Will look for polygons with 'yes' in the 'Build' attribute

#######################################################################################################################
#Some Naming stuff
inputCoreFDSName = inputFDSName.split(".")[-1]  # Cut off anything before the last period
inputFDSNameWOInitials = NCGMPname(inputCoreFDSName,inputPrefixLength)[0]
prefixInitials = NCGMPname(inputCoreFDSName,inputPrefixLength)[1]
print("Prefix name: "+prefixInitials)

#######################################################################################################################
# Create a new GDB
timeDateString = datetimePrint()[0] # Gets time and date to add to export
print("Current Run: " + timeDateString)

#Export names and proj
exportGDBName = exportGDBPrefix + timeDateString
spatialRef = arcpy.Describe(inputFDSFullPath).spatialReference

exportGDBFullPath = exportFolder + "\\" + exportGDBName + ".gdb"
print("Creating a new GDB at: "+exportGDBFullPath)
arcpy.CreateFileGDB_management(out_folder_path=exportFolder,
                               out_name=exportGDBName,
                               out_version="CURRENT")
#Create a FDS
arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                      out_name=inputCoreFDSName,
                                      spatial_reference=spatialRef)

exportFDSFullPath = exportGDBFullPath + "\\" + inputCoreFDSName
print("Created a new FDS at: "+exportFDSFullPath)

exportFDSFullPathNew = exportGDBFullPath + "\\" + exportFDSPrefix + inputFDSNameWOInitials

print("Starting to copy everything over...")
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
print("Finding active boundaries...")
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
#print(listFCsToRename)
for fcToRename in listFCsToRename:
    print ("Renaming: " + fcToRename)
    arcpy.Rename_management(in_data=exportFDSFullPathNew + "\\" + prefixInitials + fcToRename,
                              out_data=exportFDSFullPathNew + "\\" + fcToRename)

#######################################################################################################################
#OPTIONS
print("--------------------------------------------")
if buildPolygons:
    print("Building polygons...")
    #Build polygons lines MUST be labeled ContactsAndFault and points MapUnitPoints
    arcpy.FeatureToPolygon_management(in_features=exportFDSFullPathNew+"\\"+'ContactsAndFaults',
                                          out_feature_class=exportFDSFullPathNew+"\\"+'MapUnitPolys',
                                          cluster_tolerance="#",
                                          attributes="ATTRIBUTES",
                                          label_features=exportFDSFullPathNew+"\\"+'MapUnitPoints')

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

if dropFields:
    print("Drop fields...")
    for x, fctodrop in enumerate(listFCsToDropFldsFrom):
        #print(fctodrop)
        fcFullPath = exportFDSFullPathNew + "\\" + fctodrop
        #print(" " + fcFullPath)
        #print("  Disabling Editor Tracking")
        # Disable editor tracking for all feature classes, otherwise you can't delete those fields
        arcpy.DisableEditorTracking_management(fcFullPath, "DISABLE_CREATOR", "DISABLE_CREATION_DATE",
                                               "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
        listfields=arcpy.ListFields(fcFullPath, listFieldToDrop[x])
        if len(listfields) > 0:
            print("  Removing fields from: " + fctodrop )
            arcpy.DeleteField_management(fcFullPath, listFieldToDrop[x])

if nullFields:
    print("Null out fields...")
    for s, fctonull in enumerate(listFCsToNull):
        print(" Feature class to null: " + fctonull)
        fcFullPathN = exportFDSFullPathNew + "\\" + fctonull
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
    print("Add extra tables...")
    for extraTable in listExtraTables:
        arcpy.Copy_management(inputExtraTablePathGDB + "\\" + extraTable, exportGDBFullPath + "\\" + extraTable)
        print ("  Copying " + extraTable)

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
            fcpath = exportFDSFullPathNew + "\\" + finalfc
            print("   Feature Class for field renaming: " + finalfc)
            fieldsToRename = arcpy.ListFields(fcpath)
            for numb, field in enumerate(fieldsToRename):  # TODO no nead to enumerate
                #print(field.name)
                if field.name in sdeFieldNames:
                    newfieldname = gemsFieldNames[sdeFieldNames.index(field.name)]
                    arcpy.AlterField_management(fcpath, field.name,"zzzz")  # Without this simple case changes are not always recognized
                    arcpy.AlterField_management(fcpath, "zzzz", newfieldname)
                    print("     >" + field.name + " renamed to: " + newfieldname)
                #This did not work can't add a second OBJECTID field regardless of case
                # elif field.name == "objectid":
                #     print("     >Copying objectid to OBJECTID")
                #     arcpy.AddField_management(fcpath,"OBJECTID","SHORT")
                #     arcpy.CalculateField_management(fcpath, "OBJECTID","[objectid]")
                else:
                    print("      Did not need to rename: " + field.name)
            fieldsforLocConf = arcpy.ListFields(fcpath)
            #TODO change the type of LocantionConfidenceMeters in the db
            # for field in fieldsforLocConf:
            #     if field.name == "LocationConfidenceMeters":
            #         arcpy.AlterField_management(in_table=fcpath, field=field.name, field_type='FLOAT')

if crossWalkFields:
    print("Crosswalking fields...")
    arcpy.ImportToolbox(r"\\Igswzcwwgsrio\loco\Team\Crow\_Python\GEMS_Tools\GeMS_ToolsArc10.tbx")
    for finalfds2 in listFDSInGDB:
        listFCsinFinalFDS2 = arcpy.ListFeatureClasses(feature_dataset=finalfds2)
        for finalfc2 in listFCsinFinalFDS2:
            fcpath2 = exportGDBFullPath + "\\" + finalfds2 + "\\" + finalfc2
            #print(finalfc2)
            if finalfc2 in listFCsSwitchTypeAndSymbol:
                print(" Switching Type to Symbol for: " +finalfc2)
                arcpy.CalculateField_management(fcpath2, "Symbol", "[Type]")

    arcpy.AttributeByKeyValues_GEMS(exportGDBFullPath, txtFile, True)

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
    print("Building Glossary table...")
    dfG = pandas.read_excel(glossaryTable)
    master_Terms = dfG['Term'].values.tolist()
    master_Definitions = dfG['Definition'].values.tolist()
    master_DefinitionSouces = dfG['DefinitionSourceID'].values.tolist()
    arcpy.env.workspace = exportFDSFullPathNew
    listFCs = arcpy.ListFeatureClasses() #Only works in the Geologic Map FDS
    TermsInMap = set([])
    Terms = ["Type"] #Expand this to look for other needed Glossary Terms if Needed
    #Currently focused on finding "Type" in ContactsAndFaults
    for fc in listFCs:
        for term in Terms:
            if len(arcpy.ListFields(fc, term)) > 0:
                print(" "+str(fc) + " has field: " + term)
                arcpy.Frequency_analysis(fc, "in_memory/freq", term)
                with arcpy.da.SearchCursor("in_memory/freq", term) as cursor:
                    for row in cursor:
                        TermsInMap.add(row[0])
                    # print("  "+str(row[0]))
    # print(DataSourcesInMap)

    # Make a copy og the reference table
    arcpy.Copy_management(exampleBlankGlossaryTable, exportGDBFullPath + "//" + "Glossary")
    # Create some blank lists for filling
    ForTable_Terms = []
    ForTable_Def = []
    ForTable_GSources = []
    ForTable_MissingTerms = []
    for terminmap in TermsInMap:
        if terminmap  in master_Terms:
            print("   Term: " + terminmap + " is in master!")
            index = master_Terms.index(terminmap)
            ForTable_Def.append(master_Definitions[index])
            ForTable_GSources.append(master_DefinitionSouces[index])
            ForTable_Terms.append(terminmap)
        else:
            print("  >Term: " + terminmap + " is NOT in the master. Update!!!")
            ForTable_MissingTerms.append(terminmap)
    # Update the table
    # Assumes/requires GEMS field names
    cursor = arcpy.da.InsertCursor(exportGDBFullPath + "\\" + "Glossary", ['Term', 'Definition','DefinitionSourceID'])
    for i, item in enumerate(ForTable_Terms):
        cursor.insertRow([ForTable_Terms[i], ForTable_Def[i], ForTable_GSources[i]])
    del cursor

    if len(ForTable_MissingTerms) > 0:
        # Add the missing datasourceIDs
        cursor2 = arcpy.da.InsertCursor(exportGDBFullPath + "\\" + "Glossary", ['Term'])
        for x, item2 in enumerate(ForTable_MissingTerms):
            cursor2.insertRow([ForTable_MissingTerms[x]])
        del cursor2

if buildDataSources:
    print("Building DataSources table...")
    # Merge all the footprints to get a master list of datasources
    mergedFCs = r"in_memory\mergedFCs"
    arcpy.Merge_management([miscMaps, quadMaps, stateMaps, thesisMaps], mergedFCs)
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

    print(master_DataSourceID)
    print(master_Reference)

    # List all the FCs in the map or db
    arcpy.env.workspace = exportFDSFullPathNew
    #print(arcpy.env.workspace)
    listFCs = arcpy.ListFeatureClasses()
    arcpy.env.workspace = exportGDBFullPath
    listTables = arcpy.ListTables()
    listToGoThrough = listFCs + listTables
    #print(listToGoThrough)

    # Remove FCs to ignore
    for fctoignore in listFCsToIgnore:
        if fctoignore in listToGoThrough:
            listToGoThrough.remove(fctoignore)
            print(" Ignore: " + fctoignore)
    # print(listFCs)

    # Generate a list (set) with all the datasourceids
    DataSourcesInMap = set([])
    for fc in listToGoThrough:
        for datasourcename in dataSourceFieldNames:
            if len(arcpy.ListFields(fc, datasourcename)) > 0:
                print(" "+str(fc) + " has field: " + datasourcename)
                arcpy.Frequency_analysis(fc, "in_memory/freq", datasourcename)
                with arcpy.da.SearchCursor("in_memory/freq", datasourcename) as cursor:
                    for row in cursor:
                        DataSourcesInMap.add(row[0])
                    # print("  "+str(row[0]))
    # print(DataSourcesInMap)

    # Make a copy og the reference table
    arcpy.Copy_management(exampleBlankDataSourceTable, exportGDBFullPath + "//" + "DataSources")
    # Create some blank lists for filling
    ForTable_Source = []
    ForTable_URL = []
    ForTable_DataSources = []
    ForTable_MissingDataSources = []
    for dataSource in DataSourcesInMap:
        #This assumes that FGDC-STD-013-2006 will be in the table when it's copied over - don't put it in again
        if dataSource in master_DataSourceID and dataSource <> "FGDC-STD-013-2006":
            print("   Data source: " + dataSource + " is in master!")
            index = master_DataSourceID.index(dataSource)
            ForTable_Source.append(master_Reference[index])
            ForTable_URL.append(master_URL[index])
            ForTable_DataSources.append(dataSource)
        elif dataSource <> "FGDC-STD-013-2006":
            print("  >Data source: " + dataSource + " is NOT in the master. Update!!!")
            ForTable_MissingDataSources.append(dataSource)
        else:
            print("   Data source: FGDC-STD-013-2006 being ignored")

    # Update the table
    # Assumes/requires GEMS field names
    cursor = arcpy.da.InsertCursor(exportGDBFullPath + "\\" + "DataSources", ['Source', 'URL', 'DataSources_ID'])
    for i, item in enumerate(ForTable_DataSources):
        cursor.insertRow([ForTable_Source[i], ForTable_URL[i], ForTable_DataSources[i]])
    del cursor

    if len(ForTable_MissingDataSources) > 0:
        # Add the missing datasourceIDs
        cursor2 = arcpy.da.InsertCursor(exportGDBFullPath + "\\" + "DataSources", ['DataSources_ID'])
        for x, item2 in enumerate(ForTable_MissingDataSources):
            cursor2.insertRow([ForTable_MissingDataSources[x]])
        del cursor2

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
    arcpy.ImportToolbox(r"\\Igswzcwwgsrio\loco\Team\Crow\_Python\GEMS_Tools\GeMS_ToolsArc10.tbx")
    arcpy.SetIDvalues2_GEMS(Input_GeMS_style_geodatabase=exportGDBFullPath,Use_GUIDs="false", Do_not_reset_DataSource_IDs="true")

if validateDataBase:
    print("Validating the database...")
    arcpy.ImportToolbox(r"\\Igswzcwwgsrio\loco\Team\Crow\_Python\GEMS_Tools\GeMS_ToolsArc10.tbx")
    arcpy.ValidateDatabase_GEMS(
        Input_geodatabase=exportGDBFullPath,
        Output_workspace="")

arcpy.env.overwriteOutput = False


