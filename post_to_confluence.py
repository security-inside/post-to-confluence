##########################################################################################
#
#   File: post_to_confluence.py
#   Author: Cristóbal Espinosa
#   Versión: 1.0.0
#
#   Description: Script for upload info and file to a confluence page.
#
##########################################################################################

### Imports ##############################################################################
import requests
import json
##########################################################################################

##### Initial Params #####################################################################
# Confluence credentials
auth = '' # 'base64(<confluence_user>:<confluence_password>)'

# Confluence page vars
url = "https://<your_confluence_url>/rest/api/content/<your_page_id>"
url_attach = url + "/child/attachment"
url_download = "https://<your_confluence_url>/download/attachments/<your_page_id>/"
querystring = {"expand":"body.storage"}

headers_page = {
    'Content-Type': "application/json",
    'X-Atlassian-Token': "no-check",
    'Authorization': "Basic " + auth,
    'Cache-Control': "no-cache",
}

headers_attach = {
        'X-Atlassian-Token': "no-check",
        'Accept': "application/json",
        'Authorization': "Basic " + auth,
        'Cache-Control': "no-cache",
}

body_ini = """<ul>
   <li>
      <h2>Section title</h2>
   </li>
</ul>
<table>
   <colgroup>
      <col />
      <col />
      <col />
   </colgroup>
   <tbody>
      <tr>
         <th>ID</th>
         <th>Name</th>
         <th>File</th>
      </tr>"""

body_end = "</tbody></table>"

file_name = "file.txt"
##########################################################################################

# Main function ##########################################################################
def main():

    # Get basic Confluence params
    ##########################################################################################
    response = requests.request("GET", url, headers=headers_page, params=None)

    id = response.json()['id']
    title = response.json()['title']
    space = response.json()['space']['key']
    version = response.json()['version']['number']
    ##########################################################################################

    # Get actual Confluence body content
    ##########################################################################################
    response = requests.request("GET", url, headers=headers_page, params=querystring)

    old_page = response.json()['body']['storage']['value']
    ##########################################################################################

    # Upload the file to Confluence
    ##########################################################################################        
    new_content = ""
    files = {'file': (file_name, open(file_name, 'rb'), 'multipart/form-data')}

    response = requests.request("POST", url_attach, files=files, headers=headers_attach)

    new_content = new_content + """<tr>
                        <td>
                            <p>1</p>
                        </td>
                        <td>
                            <p>File</p>
                        </td>
                        <td>
                            <div class=\"content-wrapper\">
                            <p>
                                <ac:link>
                                    <ri:attachment ri:filename=\"""" + file_name + """\"/>
                                </ac:link>
                            </p>
                            </div>
                        </td>
                    </tr>"""

    # Build new version of Confluence page
    payload = {
        "id": id,
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body":{
            "storage":{
                "value": body_ini + new_content + body_end + "<br/>" + old_page,
                "representation": "storage"
            }
        },
        "version": {"number": version+1}
    }

    # Put the new version
    response = requests.request("PUT", url, data=json.dumps(payload), headers=headers_page)    

##########################################################################################

# Preconditions and validations ##########################################################
if __name__ == "__main__":
    main()
##########################################################################################