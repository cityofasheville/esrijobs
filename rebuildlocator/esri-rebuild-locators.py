#Manage Versions
import arcpy
import pprint
import os
from arcpy import env
import yaml
import logging
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
def createLocator(locator):
    arcpy.RebuildAddressLocator_geocoding(locator)

#rebuild geocoder
def rebuildLocator(locator):
    print "Rebuilding the locator: " + locator + "."
    try:
        arcpy.RebuildAddressLocator_geocoding(locator)
        print "Succcesfully Rebuild the locator: " + locator + "."
    except:
        log.error('Error rebuilding geoccoder : ' + locator + '.  ' + arcpy.GetMessages(2))


def publishLocator(info):
    #Overwrite any existing outputs

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

    print "Starting to public the geocode service " + service_name  + "."

    #stagging
    out_service_definition = info['out_service_definition']

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
            # Execute UploadServiceDefinition to publish the service definition file as a service
            arcpy.server.UploadServiceDefinition(out_service_definition, connection_file_path)
            print "The geocode service " + service_name  + "was successfully published"
        except arcpy.ExecuteError as ex:
            log.error ("An error occured " + arcpy.GetMessages(2))

    else:
        # if the sddraft analysis contained errors, display them
        log.error( "Error were returned when creating service definition draft" + analyze_messages['errors'] )

#get yaml configuration file
with open("config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#traverse yaml create sde conenction string to remove,create, and alter versions
connections =  cfg['sde_connections']
geocoder = cfg['geocoder']
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

#Create
for k in geocoder:
#loop version keys and re-create versions
    if 'in_address_locator' in k:
        if k['in_address_locator'] is not None:
            rebuildLocator( k['in_address_locator'] )
            publishLocator(k)
