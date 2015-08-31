#Manage Versions
import arcpy
import pprint
import os,sys, re
from arcpy import env
import yaml
import logging
import time
from logging import handlers

# create logger with
logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)


#setup loggin from config.yaml
def emaillogger( configkey ):
  MAILHOST = configkey['email-server']
  FROM = configkey['email-to']
  TO = configkey['email-to']
  SUBJECT = configkey['email-subject']

  smtpHandler =  logging.handlers.SMTPHandler(MAILHOST, FROM, TO, SUBJECT)

  infolog = logging.FileHandler('sde_versions.log')
  infolog.setLevel(logging.ERROR)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  infolog.setFormatter(formatter)

  LOG = logging.getLogger()
  LOG.addHandler(smtpHandler)

  logger.addHandler(infolog)
  logger.addHandler(LOG)

#delete sde connections
def deleteconn(configkey):
  #delte existing sde file if it exsists
  if configkey['out_folder_path'] is None:
    os.path.exists(configkey['out_name']) and os.remove(configkey['out_name'])
  else:
    os.path.exists(configkey['out_folder_path']+configkey['out_name']) and os.remove(configkey['out_folder_path']+configkey['out_name'])

#create sde connections from config.yaml
def connags( configkey ):
  #delete connection
  deleteconn(configkey)
  #arcpy create ags connections
  arcpy.mapping.CreateGISServerConnectionFile ( configkey['connection_type'],
                                        configkey['out_folder_path'],
                                        configkey['out_name'],
                                        configkey['server_url'],
                                        configkey['server_type'],
                                        configkey['use_arcgis_desktop_staging_folder'],
                                        configkey['staging_folder_path'],
                                        configkey['username'],
                                        configkey['password'],
                                        configkey['save_username_password'])

#create sde connections from config.yaml
def connsde( configkey ):
  #delete connection
  deleteconn(configkey)
  #arcpy create connection
  arcpy.CreateDatabaseConnection_management(configkey['out_folder_path'],
                                            configkey['out_name'],
                                            configkey['database_platform'],
                                            configkey['instance'],
                                            configkey['account_authentication'],
                                            configkey['username'],
                                            configkey['password'],
                                            configkey['save_user_pass'],
                                            configkey['database'],
                                            configkey['schema'],
                                            configkey['version_type'],
                                            configkey['version'],
                                            configkey['date'])

#create geocoder
def createLocator(info):
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = info['workspace']

    in_address_locator_style = info['in_address_locator_style']
    in_reference_data = info['in_reference_data']
    in_field_map = info['in_field_map']
    out_address_locator = info['loc_path']
    config_keyword = info['config_keyword']
    in_data = info['in_data']

    print "removing temp files."

    if os.path.isfile( out_address_locator+'.loc' ):
        os.remove(out_address_locator+'.loc')

    if os.path.isfile( out_address_locator+'.loc.xml' ):
        os.remove(out_address_locator+'.loc.xml')

    if os.path.isfile( out_address_locator+'.lox' ):
        os.remove(out_address_locator+'.lox')

    print "Creating the locator: " + out_address_locator + "."
    arcpy.ClearWorkspaceCache_management()

    try:
        arcpy.CreateAddressLocator_geocoding(in_address_locator_style, in_reference_data, in_field_map, out_address_locator, config_keyword)
        print "Succcesfully Created thelocator: " + out_address_locator + "!"
    except:
        print 'Error creating geoccoder : ' + out_address_locator + '.'
        print  arcpy.GetMessages(2)
        logger.error('Error creating geoccoder : ' + out_address_locator + '.')
        logger.error(arcpy.GetMessages(2))

    arcpy.ClearWorkspaceCache_management()
    arcpy.env.workspace = ""

#create composite
def createComposite(info):
    arcpy.env.workspace = info['workspace']
   
    in_address_locators = info['in_address_locators']
    in_field_map = info['in_field_map']
    in_selection_criteria = info['in_selection_criteria']
    out_composite_address_locator = info['out_composite_address_locator']


    print "Creating the composite locator: " + out_composite_address_locator + "."
    try:

        arcpy.CreateCompositeAddressLocator_geocoding(in_address_locators, in_field_map, in_selection_criteria, out_composite_address_locator)
        print "Succcesfully Created the composite locator: " + out_composite_address_locator + "!"
    except:
        print 'Error rebuilding compsite geoccoder : ' + out_composite_address_locator + '.'
        print  arcpy.GetMessages(2)
        logger.error('Error rebuilding compsite geoccoder : ' + out_composite_address_locator + '.')
        logger.error(arcpy.GetMessages(2))

    arcpy.ClearWorkspaceCache_management()
    arcpy.env.workspace = ""

#rebuild geocoder
def rebuildLocator(locator):
    print "Rebuilding the locator: " + locator + "."
    try:
        arcpy.RebuildAddressLocator_geocoding(locator)
        print "Succcesfully Rebuilt the locator: " + locator + "!"
    except:
        print 'Error rebuilding geoccoder : ' + locator + '.'
        print  arcpy.GetMessages(2)
        logger.error('Error rebuilding geoccoder : ' + locator + '.')
        logger.error(arcpy.GetMessages(2))

def publishLocator(info):
    #Overwrite any existing outputs
    arcpy.ClearWorkspaceCache_management()
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = info['workspace']

    loc_path = info['loc_path']
    out_sddraft = info['out_sddraft']
    service_name = info['service_name']

    server_type = info['server_type']
    connection_file_path = info['connection_file_path']
    copy_data_to_server = info['copy_data_to_server']

    folder_name =info['folder_name']
    summary = info['summary']
    tags = info['tags']
    max_candidates = info['max_candidates']

    max_batch_size = info['max_batch_size']
    suggested_batch_size = info['max_batch_size']
    supported_operations = info['supported_operations']

    #if os.path.isfile( loc_path + '.loc' ):
    if True:
        print "Starting to publish the geocode service " + service_name  + "..."

        #stagging
        out_service_definition = info['out_service_definition']

        if os.path.isfile( out_sddraft):
            os.remove(out_sddraft)

        if os.path.isfile( out_service_definition ):
            os.remove(out_service_definition)

        #Create the sd draft file
        analyze_messages  = arcpy.CreateGeocodeSDDraft (loc_path, out_sddraft, service_name,
                                        server_type, connection_file_path, copy_data_to_server,
                                        folder_name, summary, tags, max_candidates,
                                        max_batch_size, suggested_batch_size, supported_operations)

        #stage and upload the service if the sddraft analysis did not contain errors
        if analyze_messages['errors'] == {}:
            try:
                # Execute StageService to convert sddraft file to a service definition (sd) file
                arcpy.server.StageService(out_sddraft, out_service_definition)
                print "The geocode service draft " + service_name  + " was successfully created."
                print " "
            except Exception, e:
                print e.message
                print " "
                logger.error ("An error occured " + e.message)

            try:
                # Execute UploadServiceDefinition to publish the service definition file as a service
                arcpy.server.UploadServiceDefinition(out_service_definition, connection_file_path)
                print "The geocode service " + service_name  + " was successfully published."
                print " "
            except Exception, e:
                print e.message
                print " "
                logger.error ("An error occured " + e.message)

        else:
            # if the sddraft analysis contained errors, display them
            print "Error were returned when creating service definition draft "
            print analyze_messages['errors']
            print ""
            logger.error( "Error were returned when creating service definition draft " )
            logger.error( analyze_messages['errors'] )

    else:
        print "No locator found " + loc_path

    arcpy.ClearWorkspaceCache_management()
    arcpy.env.workspace = ""

#get yaml configuration file
configfile = sys.argv[1]
with open(configfile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#traverse yaml create sde conenction string to remove,create, and alter versions

connections =  cfg['sde_connections']

try:
    geocoder = cfg['geocoder']
except:
    geocoder = None

try:
    composite = cfg['composite']
except:
    composite = None

try:
    creategeo = cfg['creategeocoder']
except:
    creategeo = None


ags = cfg['ags_connections']
emails = cfg['logging']

#loop keys setup loggind
for k in emails:
    emaillogger(k)

#loop keys and create sde connection
for k in connections:
    connsde(k)

#loop keys and create ags connection
for k in ags:
    connags(k)

if creategeo is not None:
    for k in creategeo:
        if 'in_address_locator_style' in k:
            if k['in_address_locator_style'] is not None:
                createLocator( k )
                #print 'starting publish'
                publishLocator( k )

if geocoder is not None:
    for k in geocoder:
        if 'in_address_locator' in k:
            if k['in_address_locator'] is not None:
                rebuildLocator( k['in_address_locator'] )
                publishLocator(k)

if composite is not None:
    #Create
    for k in composite:
    #loop version keys and re-create versions
        if 'in_address_locators' in k:
            if k['in_address_locators'] is not None:
                createComposite( k )
                publishLocator( k )

arcpy.ClearWorkspaceCache_management()

