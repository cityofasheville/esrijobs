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
def rebuildLocator(locator):
    arcpy.RebuildAddressLocator_geocoding(locator)

def publishLocator(locator):
    #Overwrite any existing outputs
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = '/home/sde/esrijobs/rebuildlocator/files'

    locator_path = "/home/sde/esrijobs/rebuildlocator/files/address"
    sddraft_file = "/home/sde/esrijobs/rebuildlocator/files/address.sddraft"
    sd_file = "/home/sde/esrijobs/rebuildlocator/files/address.sd"
    service_name = "Address"
    summary = "Address locator for the city of Asheville"
    tags = "address, locator, geocode"
    gis_server_connection_file = "/home/sde/esrijobs/rebuildlocator/config/simplicity.ags"

    #Create the sd draft file
    analyze_messages  = arcpy.CreateGeocodeSDDraft(locator_path, sddraft_file, service_name,
                               connection_file_path=gis_server_connection_file,
                               summary=summary, tags=tags, max_result_size=20,
                               max_batch_size=500, suggested_batch_size=150)

    #stage and upload the service if the sddraft analysis did not contain errors
    #if analyze_messages['errors'] == {}:
    if True:
        try:
            # Execute StageService to convert sddraft file to a service definition (sd) file
            arcpy.server.StageService(sddraft_file, sd_file)
            # Execute UploadServiceDefinition to publish the service definition file as a service
            arcpy.server.UploadServiceDefinition(sd_file, gis_server_connection_file)
            print "The geocode service was successfully published"
        except arcpy.ExecuteError as ex:
            print "An error occured"
            print arcpy.GetMessages(2)
    else:
        # if the sddraft analysis contained errors, display them
        print "Error were returned when creating service definition draft"
        pprint.pprint(analyze_messages['errors'], indent=2)
#get yaml configuration file
with open("config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#traverse yaml create sde conenction string to remove,create, and alter versions
#for key, value in cfg.items():
connections =  cfg['sde_connections']
geocoder = cfg['geocoder']
ags = cfg['ags_connections']
emails = cfg['logging']

#loop keys setup loggind
for k in emails:
    emaillogger(k)

#loop keys and create sde connection
#for k in connections:
#    connsde(k)

#loop keys and create ags connection
for k in ags:
    connags(k)


#Create
for k in geocoder:
#loop version keys and re-create versions
    if 'in_address_locator' in k:
        if k['in_address_locator'] is not None:
#            rebuildLocator( k['in_address_locator'] )
            publishLocator(k['in_address_locator'] )
#if k['out_folder_path'] is not None:
#    #print k['out_folder_path']+k['out_name']
#    createlocator(k['out_folder_path']+k['out_name'])
#else:
#    createlocator(k['out_folder_path'])
