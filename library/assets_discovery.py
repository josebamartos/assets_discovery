#!/usr/bin/python

def main():

    ###########
    # Modules #
    ###########

    import multiprocessing
    import os
    import random
    import re
    import shutil
    import socket
    import sys
    import tempfile
    import zipfile

    module = AnsibleModule(
        argument_spec = dict(
            name = dict(required = False, default = "Ansible")
        )
    )


    #########
    # Lists #
    #########

    classifications = {
        'JBoss_4_0_0'          : 'AS 4',
        'JBoss_4_0_1_SP1'      : 'AS 4',
        'JBoss_4_0_2'          : 'AS 4',
        'JBoss_4_0_3_SP1'      : 'AS 4',
        'JBoss_4_0_4_GA'       : 'AS 4',
        'Branch_4_0'           : 'AS 4',
        'JBoss_4_2_0_GA'       : 'AS 4',
        'JBoss_4_2_1_GA'       : 'AS 4',
        'JBoss_4_2_2_GA'       : 'AS 4',
        'JBoss_4_2_3_GA'       : 'AS 4',
        'JBoss_5_0_0_GA'       : 'AS 5',
        'JBoss_5_0_1_GA'       : 'AS 5',
        'JBoss_5_1_0_GA'       : 'AS 5',
        'JBoss_6.0.0.Final'    : 'AS 6',
        'JBoss_6.1.0.Final'    : 'AS 6',
        '1.0.1.GA'             : 'AS 7',
        '1.0.2.GA'             : 'AS 7',
        '1.1.1.GA'             : 'AS 7',
        '1.2.0.CR1'            : 'AS 7',
        '1.2.0.Final'          : 'WildFly 8',
        '1.2.2.Final'          : 'WildFly 8',
        '1.2.4.Final'          : 'WildFly 8',
        '1.3.0.Beta3'          : 'WildFly 8',
        '1.3.0.Final'          : 'WildFly 8',
        '1.3.3.Final'          : 'WildFly 8',
        '1.3.4.Final'          : 'WildFly 9',
        '1.4.2.Final'          : 'WildFly 9',
        #'1.4.3.Final'          : 'WildFly 9',
        '1.4.3.Final'          : 'WildFly 10',
        '1.4.4.Final'          : 'WildFly 10',
        'JBPAPP_4_2_0_GA'      : 'EAP 4.2',
        'JBPAPP_4_2_0_GA_C'    : 'EAP 4.2',
        'JBPAPP_4_3_0_GA'      : 'EAP 4.3',
        'JBPAPP_4_3_0_GA_C'    : 'EAP 4.3',
        'JBPAPP_5_0_0_GA'      : 'EAP 5.0.0',
        'JBPAPP_5_0_1'         : 'EAP 5.0.1',
        'JBPAPP_5_1_0'         : 'EAP 5.1.0',
        'JBPAPP_5_1_1'         : 'EAP 5.1.1',
        'JBPAPP_5_1_2'         : 'EAP 5.1.2',
        'JBPAPP_5_2_0'         : 'EAP 5.2.0',
        '1.1.2.GA-redhat-1'    : 'EAP 6.0.0',
        '1.1.3.GA-redhat-1'    : 'EAP 6.0.1',
        '1.2.0.Final-redhat-1' : 'EAP 6.1.0',
        '1.2.2.Final-redhat-1' : 'EAP 6.1.1',
        '1.3.0.Final-redhat-2' : 'EAP 6.2',
        #'1.3.3.Final-redhat-1' : 'EAP 6.2',
        '1.3.3.Final-redhat-1' : 'EAP 6.3',
        '1.3.4.Final-redhat-1' : 'EAP 6.3',
        '1.3.5.Final-redhat-1' : 'EAP 6.3',
        '1.3.6.Final-redhat-1' : 'EAP 6.4',
        '1.3.7.Final-redhat-1' : 'EAP 6.4'
    }


    ####################
    # Preset Variables #
    ####################

    assets      = []
    appservers  = []
    databases   = []
    search_root = ['/etc', '/home', '/var', '/usr', '/opt', '/root']


    #############
    # Functions #
    #############

    def extract_file (archive, filename, output):
        basename = os.path.basename(filename)

        zip_stream = zipfile.ZipFile(archive)
        file_stream = open(os.path.join(output, basename),'w')

        content = zip_stream.read(filename)
        file_stream.write(content)

        zip_stream.close()
        file_stream.close()


    def get_value(filename, regexp):
        value = ""
        text = open(filename).readlines()

        for line in text:
            if re.search(regexp, line):
                value = re.search(regexp, line).group(1)

        return value


    def get_zipped_file_value (archive, filename, regexp):
        value = ""

        if sys.version_info >= (2,6):
            zip_stream = zipfile.ZipFile(archive)
            text = zip_stream.read(filename).splitlines()

            zip_stream.close()

            for line in text:
                if re.search(regexp, line):
                    value = re.search(regexp, line).group(1)

        return value


    def jboss_pretty_version(version):
        if version in classifications:
            pretty_version = classifications[version]
        else:
            pretty_version = "unknown: " + version
        return pretty_version


    def mk_dir_tmp():
        tmp_dir=os.path.join(tempfile.gettempdir(), str(random.randrange(1,999)))
        os.makedirs(tmp_dir)
        return tmp_dir


    def rm_dir(tmp_dir):
        shutil.rmtree(tmp_dir)


################
# Main program #
################

    for search_dir in search_root:
        for dirpath, dirs, files in os.walk(search_dir):
            for name in files:
                filename = os.path.join(dirpath, name)

                # Red Hat JBoss EAP 6
                if 'jboss-modules.jar' in filename and not '.installation/patches' in filename:
                    version = get_zipped_file_value(filename, 'META-INF/maven/org.jboss.modules/jboss-modules/pom.properties', 'version=(.*)')
                    pretty_version = jboss_pretty_version(version)
                    asset = {"vendor": "Red Hat", "name": "JBoss", "version": pretty_version, "path": filename}
                    appservers.append(asset)

                # Red Hat JBoss EAP < 6
                if '/jboss-as/bin/run.jar' in filename:
                    version = get_zipped_file_value(filename, 'META-INF/MANIFEST.MF', '.*[CS]V[SN]Tag=(.*) .*')
                    pretty_version = jboss_pretty_version(version)
                    asset = {"vendor": "Red Hat", "name": "JBoss", "version": pretty_version, "path": filename}
                    appservers.append(asset)

                # Oracle GlassFish 4
                if '/org.glassfish.main.admingui/war/pom.properties' in filename:
                    version = get_value(filename, 'version=(.*)')
                    asset = {"vendor": "Oracle", "name": "GlassFish", "version": version, "path": filename}
                    appservers.append(asset)

                # Oracle GlassFish 3
                if '/org.glassfish.admingui/war/pom.properties' in filename:
                    version = get_value(filename, 'version=(.*)')
                    asset = {"vendor": "Oracle", "name": "GlassFish", "version": version, "path": filename}
                    appservers.append(asset)

                # Oracle WebLogic 12
                if '/server/lib/build-versions.properties' in filename:
                    version = get_value(filename, 'version.weblogic.server.modules=(.*)')
                    asset = {"vendor": "Oracle", "name": "WebLogic", "version": version, "path": filename}
                    appservers.append(asset)

                # Oracle WebLogic 11
                if '/modules/features/weblogic.server.modules_' in filename and filename.endswith('.xml'):
                    version = get_value(filename, 'id="weblogic.server.modules" version="(.*)" xmlns="http://www.bea.com/ns/cie/feature"')
                    asset = {"vendor": "Oracle", "name": "WebLogic", "version": version, "path": filename}
                    appservers.append(asset)

                # IBM WebSphere
                if '/config/cells/' in filename and filename.endswith('server.xml'):
                    asset = {"vendor": "IBM", "name": "WebSphere", "version": "Unknown", "path": filename}
                    appservers.append(asset)

                # PostgreSQL
                if '/data/postgresql.conf' in filename:
                    asset = {"vendor": "PGDG", "name": "PostgreSQL", "version": "Unknown", "path": filename}
                    databases.append(asset)

                # MariaDB/MySQL
                if filename.endswith('/my.cnf') or filename.endswith('/my.ini'):
                    asset = {"vendor": "MariaDB/Oracle", "name": "MariaDB/MySQL", "version":"Unknown", "path": filename}
                    databases.append(asset)

                # Oracle Database
                if '/bin/dbca' in filename:
                    asset = {"vendor": "Oracle", "name": "Database", "version":"Unknown", "path": filename}
                    databases.append(asset)

                # Microsoft SQL Server
                if '/sqlservr' in filename:
                    asset = {"vendor":"Microsoft", "name": "SQL Server", "version": "Unknown", "path": filename}
                    databases.append(asset)

    module.exit_json(
        appservers = appservers,
        databases  = databases
    )

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
