#Manage Versions
import arcpy
import pprint
import os,sys
from datetime import datetime
from arcpy import env  
import yaml
import logging
from logging import handlers

print ''
print 'Start version management %s ' % datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

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

#create version
def createver(key,workspace):
  #loop keys for versions
  #get version name and attemp to create new version
  for k in key:
   for key in k: 
     if 'version-name' in key:
       
       #Execute CreateVersion
       #attemp to create new version
       try:
          arcpy.CreateVersion_management(workspace, k['parent-version'], k['version-name'], k['access-permission']) 
          print ' Create version: %s' %  k['version-name']
       except:
          log.error("Create version " +  k['version-name'] + " Failed.")
       
       #Alter Version
       #attemp to alter version
       try:
         arcpy.AlterVersion_management(workspace,  k['version-name'],  k['version-name'], 'version for: '+ k['version-name'], k['access-permission'])
       except:
         logger.error("Alter version " +  k['version-name'] + " Failed.")

#delete version
def deletever(key,workspace):
  #loop keys for versions
  #get version name and attemp to delete version
  for k in key:
   for key in k:
     if 'version-name' in key:
      try:
         arcpy.DeleteVersion_management(workspace, k['version-name'],) 
         print ' Delete version: %s' %  k['version-name']
      except:
         logger.error("Delete version " +  k['version-name'] + " Failed.")

#delete sde connections 
def deleteconn(configkey):
  #delte existing sde file if it exsists
  print 'Delete Connections.'
  if configkey['out_folder_path'] is None:
    os.path.exists(configkey['out_name']) and os.remove(configkey['out_name'])
    print ' Delet connection: %s' % configkey['out_name']
  else:
    os.path.exists(configkey['out_folder_path']+configkey['out_name']) and os.remove(configkey['out_folder_path']+configkey['out_name'])

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
#get yaml configuration file
configfile = sys.argv[1]
with open(configfile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#traverse yaml create sde conenction string to remove,create, and alter versions
connections =  cfg['sde_connections']
emails = cfg['logging']

#loop keys setup loggind
for k in emails:
  emaillogger(k)
  
#loop keys and create sde connection
for k in connections:
  connsde(k)

#delete
for k in connections:
  print 'Start Delete versions.'
  #loop version keys and delete versions if the exist
  if  'versions' in k:
    ver = k['versions']
    if k['out_folder_path'] is not None:
      deletever(ver,k['out_folder_path']+k['out_name'])
    else:
      deletever(ver,k['out_name'])
 
#compress
for k in connections:
    print 'Start Compress versions.'
    print k['out_name']
    #loop version keys and compress sde this compress state tree
    if k['out_folder_path'] is not None:
      try:
        arcpy.Compress_management(k['out_folder_path']+k['out_name'])
        arcpy.Compress_management(k['out_folder_path']+k['out_name'])
        arcpy.Compress_management(k['out_folder_path']+k['out_name'])
      except:
        logger.error("Compress version " +  k['out_folder_path']+k['out_name']  + " Failed.")
    else:
      try:
        arcpy.Compress_management(k['out_name'])
      except:
        logger.error("Compress version " +  k['out_name'] + " Failed.")

#Create
for k in connections:
  print 'Start Create versions.'
  #loop version keys and re-create versions
  if  'versions' in k:
    ver = k['versions']
    if k['out_folder_path'] is not None:
      createver(ver,k['out_folder_path']+k['out_name'])
    else:
      createver(ver,k['out_name']) 

print 'End version management %s ' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print ''

