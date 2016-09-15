#!powershell
# <license>

# WANT_JSON
# POWERSHELL_COMMON

[Reflection.Assembly]::LoadWithPartialName( "System.IO.Compression.FileSystem" ) > Out-Null

$module = New-Object psobject @{
    changed = $false
};


#########
# Lists #
#########

$jboss_classifications = @{
    'JBoss_4_0_0'           = 'AS 4';
    'JBoss_4_0_1_SP1'       = 'AS 4';
    'JBoss_4_0_2'           = 'AS 4';
    'JBoss_4_0_3_SP1'       = 'AS 4';
    'JBoss_4_0_4_GA'        = 'AS 4';
    'Branch_4_0'            = 'AS 4';
    'JBoss_4_2_0_GA'        = 'AS 4';
    'JBoss_4_2_1_GA'        = 'AS 4';
    'JBoss_4_2_2_GA'        = 'AS 4';
    'JBoss_4_2_3_GA'        = 'AS 4';
    'JBoss_5_0_0_GA'        = 'AS 5';
    'JBoss_5_0_1_GA'        = 'AS 5';
    'JBoss_5_1_0_GA'        = 'AS 5';
    'JBoss_6.0.0.Final'     = 'AS 6';
    'JBoss_6.1.0.Final'     = 'AS 6';
    '1.0.1.GA'              = 'AS 7';
    '1.0.2.GA'              = 'AS 7';
    '1.1.1.GA'              = 'AS 7';
    '1.2.0.CR1'             = 'AS 7';
    '1.2.0.Final'           = 'WildFly 8';
    '1.2.2.Final'           = 'WildFly 8';
    '1.2.4.Final'           = 'WildFly 8';
    '1.3.0.Beta3'           = 'WildFly 8';
    '1.3.0.Final'           = 'WildFly 8';
    '1.3.3.Final'           = 'WildFly 8';
    '1.3.4.Final'           = 'WildFly 9';
    '1.4.2.Final'           = 'WildFly 9';
#    '1.4.3.Final'           = 'WildFly 9';
    '1.4.3.Final'           = 'WildFly 10';
    '1.4.4.Final'           = 'WildFly 10';
    'JBPAPP_4_2_0_GA'       = 'EAP 4.2';
    'JBPAPP_4_2_0_GA_C'     = 'EAP 4.2';
    'JBPAPP_4_3_0_GA'       = 'EAP 4.3';
    'JBPAPP_4_3_0_GA_C'     = 'EAP 4.3';
    'JBPAPP_5_0_0_GA'       = 'EAP 5.0.0';
    'JBPAPP_5_0_1'          = 'EAP 5.0.1';
    'JBPAPP_5_1_0'          = 'EAP 5.1.0';
    'JBPAPP_5_1_1'          = 'EAP 5.1.1';
    'JBPAPP_5_1_2'          = 'EAP 5.1.2';
    'JBPAPP_5_2_0'          = 'EAP 5.2.0';
    '1.1.2.GA-redhat-1'     = 'EAP 6.0.0';
    '1.1.3.GA-redhat-1'     = 'EAP 6.0.1';
    '1.2.0.Final-redhat-1'  = 'EAP 6.1.0';
    '1.2.2.Final-redhat-1'  = 'EAP 6.1.1';
    '1.3.0.Final-redhat-2'  = 'EAP 6.2';
#    '1.3.3.Final-redhat-1'  = 'EAP 6.2';
    '1.3.3.Final-redhat-1'  = 'EAP 6.3';
    '1.3.4.Final-redhat-1'  = 'EAP 6.3';
    '1.3.5.Final-redhat-1'  = 'EAP 6.3';
    '1.3.6.Final-redhat-1'  = 'EAP 6.4';
    '1.3.7.Final-redhat-1'  = 'EAP 6.4'
}


####################
# Preset variables #
####################

$appservers = @()
$databases  = @()
$search_root = @(Get-WmiObject Win32_Volume -Filter "DriveType='3'"|select -expand driveletter)


#############
# Functions #
#############

function extract_file ($archive, $filename, $output){
    $basename = $filename.split('/')[-1]

    $zip_stream = [System.IO.Compression.ZipFile]::OpenRead($archive)
    $file_stream = New-Object IO.FileStream ("$output\$basename") ,'Append','Write','Read'
    
    $content = $zip_stream.GetEntry($filename).Open()
    $content.CopyTo($file_stream)

    $content.Close()
    $zip_stream.Dispose()
    $file_stream.Close()
}


function get_value($file, $regexp){
    $value = ""
    $text = Get-Content $file

    foreach ($line in $text){
        if ([regex]::Match($line, $regexp).Success){
            $value = [regex]::Match($line, $regexp).Groups[1].toString()
        }
    }
    return $value
}

function get_zipped_file_value ($archive, $filename, $regexp){
    $value = ""
    $zip_stream = [System.IO.Compression.ZipFile]::OpenRead($archive)
    $mem_stream = new-object IO.MemoryStream

    $content = $zip_stream.GetEntry($filename).Open()
    $content.CopyTo($mem_stream)
    $zip_stream.Dispose()
    $content.Close()

    $mem_stream.Position = 0
    $reader = New-Object IO.StreamReader($mem_stream)
    $text = ($reader.ReadToEnd() -split '[\r\n]') |? {$_} 

    $reader.Close()
    $mem_stream.Close()

    foreach ($line in $text){
        if ([regex]::Match($line, $regexp).Success){
            $value = [regex]::Match($line, $regexp).Groups[1].toString()
        }
    }

    return $value
}


function jboss_pretty_version($version){
    if ($jboss_classifications.ContainsKey($version)){
        $pretty_version = $jboss_classifications[$version]
    } else {
        $pretty_version = "Unknown-JBoss-Release: $version"
    }
    return $pretty_version
}


function mk_dir_tmp(){
    $tmp_dir = ($Env:Temp + "\" + (Get-Random -minimum 0 -maximum 999))
    New-Item $tmp_dir -type directory  > Out-Null
    return $tmp_dir
}

function rm_dir($tmp_dir){
    Remove-Item -Recurse -Force $tmp_dir
}


# Custom discovery of processors due to some missing facts

function get_hostname(){
    $hostname = (Get-WmiObject Win32_ComputerSystem).Name
    return $hostname
}

function get_domain(){
    $domain = (Get-WmiObject Win32_ComputerSystem).Domain
    return $domain
}

function get_ipv4(){
    $ipv4= foreach ( $i in (Get-WmiObject Win32_NetworkAdapterConfiguration -Namespace "root\CIMV2" | where { $_.IPEnabled -eq "True" } | select IPAddress) ) { $i.IPAddress[0] }
    $ipv4 = [System.String]::Join(", ", $ipv4)
    return $ipv4
}

function get_netmask(){
    $netmask = foreach ( $i in (ipconfig | Select-String "Subnet Mask" )) { ($i -split ":")[1].Trim() }
    $netmask = [System.String]::Join(", ", $netmask)
    return $netmask
}

function get_ipv6(){
    $ipv6= foreach ( $i in (Get-WmiObject Win32_NetworkAdapterConfiguration -Namespace "root\CIMV2" | where { $_.IPEnabled -eq "True" } | select IPAddress) ) { $i.IPAddress[1] }
    $ipv6 = [System.String]::Join(", ", $ipv6)
    return $ipv6
}

function get_architecture(){
    $architecture = (Get-WmiObject -Class Win32_ComputerSystem).SystemType
    return $architecture
}

function get_processor(){
    $processor = (Get-WmiObject Win32_Processor).Manufacturer[0] + " " + (Get-WmiObject Win32_Processor).Name[0]
    return $processor
}

function get_processors(){
    $processors = Get-WmiObject -Class Win32_ComputerSystem | select -ExpandProperty "NumberOfProcessors"
    return $processors
}

function get_cores(){
    $cores = 0
    Get-WmiObject -Class Win32_Processor | select -ExpandProperty "NumberOfCores" | Foreach { $cores += $_}
    return $cores
}

function get_vcpus(){
    $vcpus = Get-WmiObject -Class Win32_ComputerSystem | select -ExpandProperty "NumberOfLogicalProcessors"
    return $vcpus
}

function get_mem_total(){
    $mem_total = [math]::Round((Get-WmiObject win32_OperatingSystem).TotalVisibleMemorySize / 1024)
    return $mem_total
}

function get_mem_used(){
    $mem_total = [math]::Round((Get-WmiObject win32_OperatingSystem).TotalVisibleMemorySize / 1024)
    $mem_free = [math]::Round((Get-WmiObject win32_OperatingSystem).FreePhysicalMemory / 1024)
    $mem_used = $mem_total - $mem_free
    return $mem_used
}

function get_mem_free(){
    $mem_free = [math]::Round((Get-WmiObject win32_OperatingSystem).FreePhysicalMemory / 1024)
    return $mem_free
}

function get_devices(){
    $devices = foreach ( $i in (Get-WmiObject Win32_DiskDrive)) { (($i).DeviceID -split "\\")[3] + " (" + [math]::Round(($i).Size / 1048576) / 1024 + " GB)" }
    $devices = [System.String]::Join(", ", $devices)
    $devices
}

function get_virt_type(){
    (Get-WmiObject -Class Win32_ComputerSystem).Manufacturer
}

function get_virt_role(){
    (Get-WmiObject -Class Win32_ComputerSystem).Model
}

################
# Main program #
################

foreach ($search_dir in $search_root){
    foreach ($filename in Get-ChildItem -Recurse -Path $search_dir\ | select -expand FullName){

        # Red Hat JBoss EAP 6
        if (($filename -like '*\jboss-modules.jar') -And -Not ($filename -like '*installation\patches*'))  {
            $version = get_zipped_file_value $filename 'META-INF/maven/org.jboss.modules/jboss-modules/pom.properties' '.*version=(.*)'
            $pretty_version = jboss_pretty_version $version
            $asset = @{"vendor" = "Red Hat"; "name" = "JBoss"; "version" = $pretty_version; "path" = $filename}
            $appservers += $asset

        # Red Hat JBoss EAP < 6
        } ElseIf ($filename -like '*\jboss-as\bin\run.jar') {
            $version = get_zipped_file_value $filename 'META-INF/MANIFEST.MF' '.*[CS]V[SN]Tag=(.*) .*'
            $pretty_version = jboss_pretty_version $version
            $asset = @{"vendor" = "Red Hat"; "name" = "JBoss"; "version" = $pretty_version; "path" = $filename}
            $appservers += $asset

        # Oracle GlassFish 4
        } ElseIf ($filename -like '*\org.glassfish.main.admingui\war\pom.properties') {
            $version = get_value $filename 'version=(.*)'
            $asset = @{"vendor" = "Oracle"; "name" = "GlassFish"; "version" = $version; "path" = $filename}
            $appservers += $asset

        # Oracle GlassFish 3
        } ElseIf ($filename -like '*\org.glassfish.admingui\war\pom.properties') {
            $version = get_value $filename 'version=(.*)'
            $asset = @{"vendor" = "Oracle"; "name" = "GlassFish"; "version" = $version; "path" = $filename}
            $appservers += $asset

        # Oracle WebLogic 12
        } ElseIf ($filename -like '*\server\lib\build-versions.properties') {
            $version = get_value $filename 'version.weblogic.server.modules=(.*)'
            $asset = @{"vendor" = "Oracle"; "name" = "WebLogic"; "version" = $version; "path" = $filename}
            $appservers += $asset

        # Oracle WebLogic 11
        } ElseIf ($filename -like '*\modules\features\weblogic.server.modules_*' -And $filename.EndsWith('.xml')) {
            $version = get_value $filename 'id="weblogic.server.modules" version="(.*)" xmlns="http://www.bea.com/ns/cie/feature" '
            $asset = @{"vendor" = "Oracle"; "name" = "WebLogic"; "version" = $version; "path" = $filename}
            $appservers += $asset

        # IBM WebSphere
        } ElseIf ($filename -like '*\config\cells\*' -And $filename.EndsWith('server.xml')) {
            $asset = @{"vendor" = "IBM"; "name" = "WebSphere"; "version" = $version; "path" = $filename}
            $appservers += $asset

        # PostgreSQL
        } elseif ($filename -like '*\data\postgresql.conf') {
            $asset = @{"vendor" = "PGDG"; "name" = "PostgreSQL"; "version" = "Unknown"; "path" = $filename}
            $databases += $asset

        # MariaDB/MySQL
        } elseif ($filename.endswith('my.ini') -or $filename.endswith('my.cnf')){
            $asset = @{"vendor" = "Oracle/MariaDB"; "name" = "MariaDB/MySQL"; "version" = "Unknown"; "path" = $filename}
            $databases += $asset

        # Oracle Database
        } ElseIf ($filename -like '*\bin\dbca.exe') {
            $asset = @{"vendor" = "Oracle"; "name" = "Database"; "version" = "Unknown"; "path" = $filename}
            $databases += $asset

        # Micosoft SQL Server
        } ElseIf (($filename -like '*\sqlservr.exe') -And -Not ($filename -like '*\WinSxS\*')) {
            $asset = @{"vendor" = "Microsot"; "name" = "SQL Server"; "version" = "Unknown"; "path" = $filename}
            $databases += $asset

        }
    }
}

$hostname     = get_hostname
$domain       = get_domain
$ipv4         = get_ipv4
$netmask      = get_netmask
$ipv6         = get_ipv6
$architecture = get_architecture
$processor    = get_processor
$processors   = get_processors
$cores        = get_cores
$vcpus        = get_vcpus
$swap_total   = ""
$swap_used    = ""
$swap_free    = ""
$mem_total    = get_mem_total
$mem_used     = get_mem_used
$mem_free     = get_mem_free
$drives       = get_devices
$virt_type    = get_virt_type
$virt_role    = get_virt_role

Set-Attr $module "win_hostname"            $hostname
Set-Attr $module "win_domain"              $domain
Set-Attr $module "win_all_ipv4_addresses"  $ipv4
Set-Attr $module "win_netmask"             $netmask
Set-Attr $module "win_all_ipv6_addresses"  $ipv6
Set-Attr $module "win_architecture"        $architecture
Set-Attr $module "win_processor"           $processor
Set-Attr $module "win_processor_count"     $processors
Set-Attr $module "win_processor_cores"     $cores
Set-Attr $module "win_processor_vcpus"     $vcpus
Set-Attr $module "win_swap_total"          $swap_total
Set-Attr $module "win_swap_used"           $swap_used
Set-Attr $module "win_swap_free"           $swap_free
Set-Attr $module "win_mem_total"           $mem_total
Set-Attr $module "win_mem_used"            $mem_used
Set-Attr $module "win_mem_free"            $mem_free
Set-Attr $module "win_devices"             $drives
Set-Attr $module "win_virtualization_type" $virt_type
Set-Attr $module "win_virtualization_role" $virt_role
Set-Attr $module "appservers"              $appservers
Set-Attr $module "databases"               $databases

Exit-Json $module
