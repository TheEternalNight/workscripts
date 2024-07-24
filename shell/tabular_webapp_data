# сохранение данных в виде таблицы из веб-приложения 

$uri = '172.25.181.211' ##Server URI
$port = ':8085'
$login = "_@gmail.com"   ##Admin Email
$passw = "root"    ##Admin Pass
$token = "cf15af024e0022e81e80434ef58ad271debb72ab6bd630d3faf6d98f802a66a5"
$encoding = "UTF8"

##string to MD5
$md5 = new-object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider
$utf8 = new-object -TypeName System.Text.UTF8Encoding
$passwHash = [System.BitConverter]::ToString($md5.ComputeHash($utf8.GetBytes($passw))).Replace("-","")

## Login to get the cookie for
$logonBody='{"controller":"LogonController","query":{"user":{"login":"$login","password":"$passwHash"}},"subsystems":[{"uuid":"hidden","app_version":"5.8.16"}],"app_version":"5.8.16"}'
$logonBody=$ExecutionContext.InvokeCommand.ExpandString($logonBody)
$response=Invoke-WebRequest -Uri ($uri + $port) `
-Method "POST" `
-ContentType "application/json" `
-Body $logonBody `
-SessionVariable "session"
    
## Exract and save the cookie to "session" variable
$respArray=$response.ToString() -split '"'
$cookie=New-Object System.Net.Cookie
$cookie.Name="session"
$cookie.Value=$respArray[5]
$cookie.Domain=$uri -replace "h.+://"
$session.Cookies.Add($cookie)

function Invoke-WebApi {
    
    Invoke-WebRequest -Uri ($uri + $port) `
    -Method "POST" `
    -ContentType "application/json" `
    -Body $body `
    -WebSession $session
}

function Invoke-CrocoApi {

    $responce = Invoke-WebRequest `
        -uri ($uri + $port + "/?controller=" + $apiController + "&server_token=" + $token)
    Set-Content `
    -Path ($PSScriptRoot + $outFile) `
    -Value $responce.content
}


#тело запроса для Domain_accounts (WebAPI)
$requestDomainAcc = '{"controller":"BatchProcessing","query":{"items":[{"name":"AccountTree","controller":"account_tree","params":{"name_filter":{"name":""}},"subsystems":[{"uuid":"hidden","app_version":"5.8.16"}],"app_version":"5.8.16"}]},"app_version":"5.8.16"}'

#запрос к WebAPI (Domain_accounts)
$body = $requestDomainAcc
$response = Invoke-WebApi
$response = $response.Content | ConvertFrom-Json

#Создаем/очищаем, заполняем CSV-файл (domain_acc_parsed.csv)
if(Test-Path -Path ($PSScriptRoot + '\temp\domain_acc_parsed.csv')){
    Clear-Content -Path ($PSScriptRoot + '\temp\domain_acc_parsed.csv')
}

Add-Content -Encoding $encoding -Path ($PSScriptRoot + '\temp\domain_acc_parsed.csv') -Value '"display_name","login","AD(display_name)","last_activity_utc_time"'
$response.result.AccountTree.result.root.items.items | ForEach-Object -Process {
    
    Add-Content -Encoding $encoding -Path ($PSScriptRoot + '\temp\domain_acc_parsed.csv') -Value ($_.employee.display_name + ',' + $_.login + ',' + $_.display_name + ',' + $_.last_activity_utc_time)
}


#получаем список сотрудников и OU от "api_departments"
$apiController="api_departments"
$outFile="\temp\api_deps.json"
Invoke-CrocoApi


#парсим список сотрудников и OU от "api_departments"
Start-Process ($PSScriptRoot + '\python\python.exe') `
    -PassThru `
    -ArgumentList (
        ($PSScriptRoot + '\webapiparser.py'),`
        ($PSScriptRoot + '\temp\api_deps.json'),`
        ($PSScriptRoot + '\temp\api_deps_parsed.csv')
    ) `
    | Wait-Process


#получаем список сотрудников от "api_employees"
$apiController="api_employees"
$outFile="\temp\api_employees.json"
Invoke-CrocoApi

#Создаем/очищаем, заполняем CSV-файл (api_employees_parsed.csv)
if(Test-Path -Path ($PSScriptRoot + "\temp\api_employees_parsed.csv")){
    Clear-Content -Path ($PSScriptRoot + "\temp\api_employees_parsed.csv")
}

Add-Content -Encoding $encoding -Path ($PSScriptRoot + "\temp\api_employees_parsed.csv") -Value '"employee_id","display_name","first_name","second_name"'
$parsedEmployees = Get-Content -Path ($PSScriptRoot + "\temp\api_employees.json") | ConvertFrom-Json
$parsedEmployees.items | ForEach-Object -Process {
    
    Add-Content -Encoding $encoding -Path ($PSScriptRoot + "\temp\api_employees_parsed.csv") `
    -Value ($_.employee_id.tostring() + ',' + $_.display_name + ',' + $_.first_name + ',' + $_.second_name + ',' + $_.display_name)
}


#Соединяем таблицы 
#("api_deps_parsed" и "api_employees_parsed" по значению "employee_id"
# "domain_acc_parsed" и "api_employees_parsed" по занчению "display_name"

$apiDepEmployees = Get-Content -Path ($PSScriptRoot + '\temp\api_deps_parsed.csv') | ConvertFrom-Csv

$apiEmployees = Get-Content -Path ($PSScriptRoot + "\temp\api_employees_parsed.csv") | ConvertFrom-Csv

$domainAccEmployees = Get-Content -Path ($PSScriptRoot + '\temp\domain_acc_parsed.csv') | ConvertFrom-Csv


$employees = [System.Collections.ArrayList]@()

foreach ($_ in $apiEmployees) {
    
    $displayName = $_.display_name
    $employeeId = $_.employee_id
    $displayName
    foreach ($_ in $apiDepEmployees) {
        
        if ($_.Id -eq $employeeId) {
            
            $isEnabled = $_.is_enabled
            break
        }
    }

    foreach ($_ in $domainAccEmployees) {

        if ($_.display_name.tostring() -eq $displayName.ToString()){
            
            $login = $_.login
            $lastActivity = $_.last_activity_utc_time
            break        
        }
    }

    $employees.Add( 
                    [PSCustomObject]@{
                    employee_id = $employeeId
                    display_name = $displayName
                    login = $login
                    last_activity_utc_time = $lastActivity
                    is_enabled = $isEnabled
                    }
                  )

    $employeeId = $null
    $displayName = $null
    $login = $null
    $lastActivity = $null
    $isEnabled = $null
}

#Создаем файл "Employees.csv" с финальной таблицей

Set-Content -Encoding $encoding -Path ($PSScriptRoot +"\Employees.csv") -Value ($employees | ConvertTo-Csv | select -Skip 1)

Add-Content -Encoding $encoding -Path ($PSScriptRoot + "\temp\log.txt") -Value ((Get-Date).ToString() + ":" + $Error)
