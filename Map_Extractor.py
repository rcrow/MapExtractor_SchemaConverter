import arcpy
import datetime

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
listFCsToClip = ['CartographicLines','ContactsAndFaults','MapUnitLines']
#These feature classes with be "clipped" to the quad boundary using a select by location
listFCsToSelectByLocation = ['MapUnitPoints','OrientationPoints']
#Annos
listAnnos = ['MapUnitPointsAnno24k','OrientationPointsAnno24k']

#These are the feature classes that will NOT be ignored
listCoreFCs = listFCsToClip + listFCsToSelectByLocation
listFCsToRename = listFCsToSelectByLocation + listAnnos #These are not renamed during the select by location process

#######################################################################################################################
#Export destinations
exportFolder = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\Extracted_GIS_db"
exportGDBPrefix = "SMSE_"
exportFDSPrefix = "SMSE_"

#######################################################################################################################
#Options
buildPolygons = True
removeQuad = True
removeMultiParts = True

makeTopology = True
#input for makeTopology
mainLineFileName = "ContactsAndFaults"

makeTables = True
#Input FC list and field list of lists must be in the same order
listFCsForTables = ["CartographicLines",
                    "ContactsAndFaults",
                    "MapUnitPoints",
                    "MapUnitPolys",
                    "OrientationPoints",
                    "MapUnitLines"]
listFieldsForTables = [['type'],
                       ['type'],
                       ['mapunit'],
                       ['mapunit'],
                       ['type','stationid','azimuth','inclination','locationsourceid','datasourceid'],
                       ['type','mapunit']]
print("Length of FieldsForTables : " +str(len(listFieldsForTables)))

dropFields = True
listFCsToDropFldsFrom = ['CartographicLines',#1
                         'ContactsAndFaults',#2
                         'MapUnitPoints',#3
                         'MapUnitPolys',#4
                         'OrientationPoints',#5
                         'MapUnitLines']#6

#This list of lists needs to be in the same order and the above list of FCs!
listFiledToDrop = [['symbol','label','datasourceid','notes','creator','createdate','editor','editdate','datasourcenotes'],#1
                   ['isconcealed','existenceconfidence','identityconfidence','locationconfidencemeters','symbol',
                         'label','datasourceid','notes','creator','createdate','editor','editdate','datasourcenotes',
                         'checkby','checknotes','validsmall','FID_selectedQuad','FID_TempQuad','Name','Active','Build','ORIG_FID'],#2
                   ['identityconfidence','label','symbol','notes','datasourceid','mapunit2','origunit','creator',
                         'createdate','editor','editdate','datasourcenotes','facies','checkby','checknotes','validsmall'],#3
                   ['identityconfidence','label','symbol','notes','datasourceid','mapunit2','origunit','creator',
                         'createdate','editor','editdate','datasourcenotes','facies','checkby','checknotes','validsmall'],#4
                   ['mapunit','symbol','label','plotatscale','locationconfidencemeters','identityconfidence',
                      'orientationconfidencedegrees','notes','creator','createdate','editor','editdate','datasourcenotes',
                      'mapunit2','origunit','facies','locationsourceid'],#5
                   ['isconcealed','existenceconfidence','identityconfidence','locationconfidencemeters','symbol',
                         'label','datasourceid','mapunit2','origunit','creator','createdate','editor','editdate','datasourcenotes']#6
                   ]

addExtraTable = True
inputExtraTablePathGDB = r"\\Igswzcwwgsrio\loco\Team\Felger\ActiveMaps\CastleRock24k_USGS\GIS\CR24k_PostPubsReview\CR24k_Extract_20180809\CastleRock24k_20180809_1254_06.gdb"
listExtraTables = ['DataSources','DescriptionOfMapUnits']

addCMULMU = True
exportFDSCMULMU_Name = "CorrelationOfMapUnits"
inputCMULMUPathFDS = r"Database Connections\Connection to igswzcwggsmoki.wr.usgs.gov_LOCOMAPS_RCROW.sde\locomaps.dbo.SMSECorrelationOfMapUnits"

addXSEC1 = True
exportFDSXSEC1_Name = "XSection_1"
inputXSEC1PathFDS = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\SMSE_Xsec.gdb\XSectionA"

addXSEC2 = True
exportFDSXSEC2_Name = "XSection_2"
inputXSEC2PathFDS = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\SMSE_Xsec.gdb\XSectionB"

addXSEC3 = False
exportFDSXSEC3_Name = "XSection_3"
inputXSEC3PathFDS = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\SpiritMtnSE24k\SMSE_Xsec.gdb\XSectionC"

addExtraFCs = False
inputExtraFCsPathFDS = r"\\Igswzcwwgsrio\loco\Team\Felger\ActiveMaps\CastleRock24k_USGS\GIS\CR24k_PostPubsReview\CR24k_Extract_20180809\CastleRock24k_20180809_1254_06.gdb"
listExtraFCs = ['DataSourcePolys','GenericSamples','GenericSamplesAnno','MiscAnno']

addDRG = True
inputDRGRasterMosaic = r"\\igswzcwwgsrio\DataLibrary\GMEG_DataLibraryLinks\TOPOMAPS_DRG24K_AZ.lyr"

simplifyGeomorphLines = False
simpSQLGeomorphLines = " NOT type = '04.01.01' " #Selection will be deleted

simplifyOrientationPoints = True
simpSQLOrientationPoints = " NOT plotatscale = 24000 " #Selection will be deleted

#######################################################################################################################
#Input files
inputDBPath = r"Database Connections\Connection to igswzdwgdbkiva.wr.usgs.gov_RSCGEO_RCROW.sde"
inputFDSName="rscgeo.dbo.RSCGeologicMap"
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
print(listFCsToRename)
for fcToRename in listFCsToRename:
    print ("Renaming: " + fcToRename)
    arcpy.Rename_management(in_data=exportFDSFullPathNew + "\\" + prefixInitials + fcToRename,
                              out_data=exportFDSFullPathNew + "\\" + fcToRename)

#######################################################################################################################
#OPTIONS
if buildPolygons:
    #Build polygons lines MUST be labeled ContactsAndFault and points MapUnitPoints
    arcpy.FeatureToPolygon_management(in_features=exportFDSFullPathNew+"\\"+'ContactsAndFaults',
                                          out_feature_class=exportFDSFullPathNew+"\\"+'MapUnitPolys',
                                          cluster_tolerance="#",
                                          attributes="ATTRIBUTES",
                                          label_features=exportFDSFullPathNew+"\\"+'MapUnitPoints')

if simplifyGeomorphLines:
    #delete all lines except lineaments from GeomorphLines
    fcName="GeomorphLines"
    tempLayer = arcpy.MakeFeatureLayer_management(exportFDSFullPathNew + "\\" + fcName,"GMorph_lyr")
    arcpy.SelectLayerByAttribute_management(tempLayer,"NEW_SELECTION",simpSQLGeomorphLines)
    arcpy.DeleteFeatures_management(tempLayer)

if simplifyOrientationPoints:
    fcName = "OrientationPoints"
    tempLayer = arcpy.MakeFeatureLayer_management(exportFDSFullPathNew + "\\" + fcName,"Orient_lyr")
    arcpy.SelectLayerByAttribute_management(tempLayer,"NEW_SELECTION",simpSQLOrientationPoints)
    arcpy.DeleteFeatures_management(tempLayer)

if makeTopology:
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

if makeTables:
    for i, fcForTable in enumerate(listFCsForTables):
        fullPathFC = exportFDSFullPathNew + "\\" + fcForTable
        print(fullPathFC)
        for field in listFieldsForTables[i]:
            print(field)
            fullPathTable = exportGDBFullPath + "\\" + fcForTable + "_" + field
            arcpy.Frequency_analysis(fullPathFC,
                                     fullPathTable,
                                     field)

if dropFields:
    for x, fcToDrop in enumerate(listFCsToDropFldsFrom):
        print(fcToDrop)
        fcFullPath = exportFDSFullPathNew + "\\" + fcToDrop
        print("  " + fcFullPath)
        print("  Disabling Editor Tracking")
        # Disable editor tracking for all feature classes, otherwise you can't delete those fields
        arcpy.DisableEditorTracking_management(fcFullPath, "DISABLE_CREATOR", "DISABLE_CREATION_DATE",
                                               "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
        print("  Removing fields from: " + fcToDrop )
        arcpy.DeleteField_management(fcFullPath, listFiledToDrop[x])

if addExtraTable:
    for extraTable in listExtraTables:
        arcpy.Copy_management(inputExtraTablePathGDB + "\\" + extraTable, exportGDBFullPath + "\\" + extraTable)
        print ("Copying " + extraTable)

if addCMULMU:
    arcpy.Copy_management(inputCMULMUPathFDS, exportGDBFullPath + "\\" + exportFDSCMULMU_Name)

if addXSEC1:
    arcpy.Copy_management(inputXSEC1PathFDS, exportGDBFullPath + "\\" + exportFDSXSEC1_Name)

if addXSEC2:
    arcpy.Copy_management(inputXSEC2PathFDS, exportGDBFullPath + "\\" + exportFDSXSEC2_Name)

if addXSEC3:
    arcpy.Copy_management(inputXSEC3PathFDS, exportGDBFullPath + "\\" + exportFDSXSEC3_Name)

if addExtraFCs:
    for extraFC in listExtraFCs:
        arcpy.Copy_management(inputExtraFCsPathFDS + "\\" + extraFC, exportFDSFullPathNew + "\\" + extraFC)

if addDRG:
    arcpy.env.workspace = exportGDBFullPath
    arcpy.Clip_management(in_raster=inputDRGRasterMosaic,
                          out_raster="DRG",
                          in_template_dataset=quad, nodata_value="256",
                          clipping_geometry="ClippingGeometry", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

if removeQuad:
    arcpy.env.workspace = exportFDSFullPathNew
    checkAndDelete(quadLine)
    checkAndDelete(quad)
    checkAndDelete(exportFDSFullPathNew+"\\"+"QuadBoundary")

arcpy.env.overwriteOutput = False


