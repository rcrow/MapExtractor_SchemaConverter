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

def copyOnlyNeeded(inputFDSFullPath,exportFDSFullPath,exportFDSFullPathNew,inputPrefixLength,listCoreFCs):
    arcpy.env.workspace = inputFDSFullPath
    print("Workspace is: " + arcpy.env.workspace)
    listFCsInInput = arcpy.ListFeatureClasses("*")
    arcpy.env.workspace = exportFDSFullPath
    print("Workspace is: " + arcpy.env.workspace)
    listToRename = []
    for fcInInput in listFCsInInput:
        genericFileName = NCGMPname(fcInInput.split(".")[-1],inputPrefixLength)[0]
        print(" ####################")
        print("     Part: "+genericFileName)
        print("     fcInInput: " + fcInInput)
        if genericFileName in listCoreFCs:
            importPath = inputFDSFullPath+ "\\"+ fcInInput
            exportDestination = exportFDSFullPath + "\\" + fcInInput.split(".")[-1] #Export has initials
            print("     Import Path: " + importPath)
            print("     Check if exists: "+str(arcpy.Exists(importPath)))
            print("     Export Destintion: "+exportDestination)
            print("  Copying: " + fcInInput)
            arcpy.Copy_management(inputFDSFullPath+ "\\"+ fcInInput, exportDestination)
        else:
            print("  Skipping: " + fcInInput)
    arcpy.Rename_management(in_data=exportFDSFullPath,
                            out_data=exportFDSFullPathNew)
    print("Renaming FDS to: " + exportFDSFullPathNew)

arcpy.env.overwriteOutput = True
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
listFCsForTables = ["CartographicLines","ContactsAndFaults","GeomorphLines","MapUnitPoints","MapUnitPolys","OrientationPoints","MapUnitLines"]
listFieldsForTables = [['type'],['type'],['type'],['mapunit'],['mapunit'],['type','stationid','azimuth','inclination','locationsourceid','datasourceid'],['mapunit']]
print("Length of FieldsForTables : " +str(len(listFieldsForTables)))

dropFields = True
listFCsToDropFldsFrom = ['CartographicLines',
                         'ContactsAndFaults',
                         'GeomorphLines',
                         'MapUnitPoints',
                         'MapUnitPolys',
                         'OrientationPoints']
#This list of lists needs to be in the same order and the above list of FCs!
listFiledToDrop = [['symbol','label','datasourceid','notes','creator','createdate','editor','editdate','datasourcenotes'],# #1
                   ['isconcealed','existenceconfidence','identityconfidence','locationconfidencemeters','symbol',
                         'label','datasourceid','notes','creator','createdate','editor','editdate','datasourcenotes',
                         'checkby','checknotes','validsmall','FID_selectedQuad','FID_TempQuad','Name','Active','Build'],# #2
                   ['isconcealed','existenceconfidence','identityconfidence','locationconfidencemeters','symbol',
                        'label','datasourceid','notes','creator','createdate','editor','editdate','datasourcenotes'],# #3
                   ['identityconfidence','label','symbol','notes','datasourceid','mapunit2','origunit','creator',
                       'createdate','editor','editdate','datasourcenotes','facies','checkby','checknotes','validsmall'],# #4
                   ['identityconfidence','label','symbol','notes','datasourceid','mapunit2','origunit','creator',
                         'createdate','editor','editdate','datasourcenotes','facies','checkby','checknotes','validsmall'],# #5
                   ['mapunit','symbol','label','plotatscale','locationconfidencemeters','identityconfidence',
                      'orientationconfidencedegrees','notes','creator','createdate','editor','editdate','datasourcenotes',# #6
                      'mapunit2','origunit','facies']]

#######################################################################################################################
#Input files
inputSDE = r"Database Connections\Connection to igswzcwggsmoki.wr.usgs.gov_LOCOGEO_RCROW.sde"
inputFDSName="locogeo.sde.PKHGeologicMap"
inputPrefixLength = 3 #All FCs and FDS in the import should have the same prefix (or atleast the same prefix length)
inputFDSFullPath = inputSDE + "\\" + inputFDSName
print("FDS to be copied: "+inputFDSFullPath)
inquad = r"\\Igswzcwwgsrio\loco\GeologicMaps_InProgress\LOCOBigBrother\LOCOBigBrother.gdb\Focus_PKH" #Will look for polygons with 'yes' in the 'Build' attribute

#######################################################################################################################
#Input lists
#These feature classes with be "clipped" to the quad boundary with clip
listFCsToClip = ['CartographicLines','ContactsAndFaults','GeomorphLines','MapUnitLines']
#These feature classes with be "clipped" to the quad boundary using a select by location
listFCsToSelectionByLocation = ['MapUnitPoints','OrientationPoints']
#Annos
listAnnos = ['MapUnitPointsAnno24k','OrientationPointsAnno24k']

#These are the feature classes that will NOT be ignored
listCoreFCs = listFCsToClip + listFCsToSelectionByLocation
listFCsToRename = listFCsToSelectionByLocation + listAnnos #These are not renamed during the select by location process

#######################################################################################################################
#Export destinations
exportFolder = r"\\igswzcwwgsrio\loco\Team\Crow\_TestingSandbox\MapExtractor"
exportGDBPrefix = "OptTest_"
exportFDSPrefix = "Test_"

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
spatialref = arcpy.Describe(inputFDSFullPath).spatialReference

exportGDBFullPath = exportFolder + "\\" + exportGDBName + ".gdb"
print("Creating a new GDB at: "+exportGDBFullPath)
arcpy.CreateFileGDB_management(out_folder_path=exportFolder,
                               out_name=exportGDBName,
                               out_version="CURRENT")
#Create a FDS
arcpy.CreateFeatureDataset_management(out_dataset_path=exportGDBFullPath,
                                      out_name=inputCoreFDSName,
                                      spatial_reference=spatialref)

exportFDSFullPath = exportGDBFullPath + "\\" + inputCoreFDSName
print("Created a new FDS at: "+exportFDSFullPath)

exportFDSFullPathNew = exportGDBFullPath + "\\" + exportFDSPrefix + inputFDSNameWOInitials

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
    elif fcName in listFCsToSelectionByLocation:
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
if buildPolygons:
    #Build polygons lines MUST be labeled ContactsAndFault and points MapUnitPoints
    arcpy.FeatureToPolygon_management(in_features=exportFDSFullPathNew+"\\"+'ContactsAndFaults',
                                          out_feature_class=exportFDSFullPathNew+"\\"+'MapUnitPolys',
                                          cluster_tolerance="#",
                                          attributes="ATTRIBUTES",
                                          label_features=exportFDSFullPathNew+"\\"+'MapUnitPoints')
########################################################################################################################
#delete all lines except lineaments from GeomorphLines
fcName="GeomorphLines"

tempLayer = arcpy.MakeFeatureLayer_management(exportFDSFullPathNew + "\\" + fcName,"GMorph_lyr")

arcpy.SelectLayerByAttribute_management(tempLayer,"NEW_SELECTION"," NOT type = '04.01.01' ")  #Lineaments?

arcpy.DeleteFeatures_management(tempLayer)

#######################################################################################################################
if removeQuad:
    arcpy.env.workspace = exportFDSFullPathNew
    checkAndDelete(quadLine)
    checkAndDelete(quad)
    checkAndDelete(exportFDSFullPathNew+"\\"+"QuadBoundary")

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

arcpy.env.overwriteOutput = False


