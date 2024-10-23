import os
import ssl
import certifi
import requests
import json
import xmlrpc.client
from requests.auth import HTTPBasicAuth
from datetime import datetime
from datetime import date
from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

ssl_context = ssl.create_default_context(cafile=certifi.where())
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
slack_app_token = os.environ['SLACK_APP_TOKEN']

client = WebClient(token=slack_bot_token, ssl=ssl_context)
app = App(client = client)

# Dictionary to store values
user_view_ids = {}
user_env_selection = {}
user_webhook_id_selection = {}

details_modal = {
        "type": "modal",
        "callback_id": "webhook_details",
        "title": {
            "type": "plain_text",
            "text": "Webhook Details"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Webhook"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "$YOUR POLICY INFO$",
                }
            },
            {
                "type": "input",
                "block_id": "webhook_url_input",
                "label": {
                    "type": "plain_text",
                    "text": "Webhook URL"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "webhook_url"
                }
            },
            {
                "type": "input",
                "block_id": "jql_input",
                "label": {
                    "type": "plain_text",
                    "text": "JQL Filter"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "jql"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*<https://$YOUR JIRA DEV URL$/issues/?jql=|해당 링크> 에서 실제 검색 가능한 JQL인지 검증 필수입니다.*",
                }
            },
            # First group of events - for issues
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_1",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Issues"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_1",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Issue Created"}, "value": "jira:issue_created"},
                        {"text": {"type": "plain_text", "text": "Issue Updated"}, "value": "jira:issue_updated"},
                        {"text": {"type": "plain_text", "text": "Issue Deleted"}, "value": "jira:issue_deleted"},
                        {"text": {"type": "plain_text", "text": "Issue worklog changed"}, "value": "jira:worklog_updated"}
                    ]
                }
            },
            # Second group of events - for worklogs
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_2",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Worklogs"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_2",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Worklog Created"}, "value": "worklog_created"},
                        {"text": {"type": "plain_text", "text": "Worklog Updated"}, "value": "worklog_updated"},
                        {"text": {"type": "plain_text", "text": "Worklog Deleted"}, "value": "worklog_deleted"}
                    ]
                }
            },
            # Third group of events - for comments
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_3",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Comments"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_3",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Comment Added"}, "value": "comment_created"},
                        {"text": {"type": "plain_text", "text": "Comment Edited"}, "value": "comment_updated"},
                        {"text": {"type": "plain_text", "text": "Comment Deleted"}, "value": "comment_deleted"}
                    ]
                }
            },
            # Fourth group of events - for issue links
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_4",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Issue Links"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_4",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Issue Link Created"}, "value": "issuelink_created"},
                        {"text": {"type": "plain_text", "text": "Issue Link Deleted"}, "value": "issuelink_deleted"}
                    ]
                }
            }
        ]
    }

details_modal_prod = {
        "type": "modal",
        "callback_id": "webhook_details",
        "title": {
            "type": "plain_text",
            "text": "Webhook Details"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Webhook"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "$YOUR POLICY INFO$",
                }
            },
            {
                "type": "input",
                "block_id": "dev_jira_key_input",
                "label": {
                    "type": "plain_text",
                    "text": "Dev Jira Key"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "dev_jira_key"
                }
            },
            {
                "type": "input",
                "block_id": "webhook_url_input",
                "label": {
                    "type": "plain_text",
                    "text": "Webhook URL"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "webhook_url"
                }
            },
            {
                "type": "input",
                "block_id": "jql_input",
                "label": {
                    "type": "plain_text",
                    "text": "JQL Filter"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "jql"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*<https://$YOUR JIRA URL$/issues/?jql=|해당 링크> 에서 실제 검색 가능한 JQL인지 검증 필수입니다.*",
                }
            },
            # First group of events - for issues
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_1",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Issues"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_1",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Issue Created"}, "value": "jira:issue_created"},
                        {"text": {"type": "plain_text", "text": "Issue Updated"}, "value": "jira:issue_updated"},
                        {"text": {"type": "plain_text", "text": "Issue Deleted"}, "value": "jira:issue_deleted"},
                        {"text": {"type": "plain_text", "text": "Issue worklog changed"}, "value": "jira:worklog_updated"}
                    ]
                }
            },
            # Second group of events - for worklogs
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_2",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Worklogs"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_2",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Worklog Created"}, "value": "worklog_created"},
                        {"text": {"type": "plain_text", "text": "Worklog Updated"}, "value": "worklog_updated"},
                        {"text": {"type": "plain_text", "text": "Worklog Deleted"}, "value": "worklog_deleted"}
                    ]
                }
            },
            # Third group of events - for comments
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_3",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Comments"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_3",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Comment Added"}, "value": "comment_created"},
                        {"text": {"type": "plain_text", "text": "Comment Edited"}, "value": "comment_updated"},
                        {"text": {"type": "plain_text", "text": "Comment Deleted"}, "value": "comment_deleted"}
                    ]
                }
            },
            # Fourth group of events - for issue links
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_4",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Issue Links"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_4",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Issue Link Created"}, "value": "issuelink_created"},
                        {"text": {"type": "plain_text", "text": "Issue Link Deleted"}, "value": "issuelink_deleted"}
                    ]
                }
            }
        ]
    }

# Create a global variable to store the initial modal view with only a confirm button
jira_initial_password_reset_modal = {
    "type": "modal",
    "callback_id": "password_reset_modal",
    "title": {
        "type": "plain_text",
        "text": "Password Reset",
    },
    "blocks": [
        {
            "type": "section",
            "block_id": "confirm_block",
            "text": {
                "type": "mrkdwn",
                "text": "정말 비밀번호를 초기화 하시겠습니까? \n진행하려면 Confirm 버튼을 눌러주세요.",
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Confirm",
                },
                "style": "primary",  # Use "primary" style for green color
                "action_id": "jira_confirm_reset",
            },
        },
    ],
}

# Create a global variable to store the initial modal view with only a confirm button
wiki_initial_password_reset_modal = {
    "type": "modal",
    "callback_id": "password_reset_modal",
    "title": {
        "type": "plain_text",
        "text": "Password Reset",
    },
    "blocks": [
        {
            "type": "section",
            "block_id": "confirm_block",
            "text": {
                "type": "mrkdwn",
                "text": "정말 비밀번호를 초기화 하시겠습니까? \n진행하려면 Confirm 버튼을 눌러주세요.",
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Confirm",
                },
                "style": "primary",  # Use "primary" style for green color.
                "action_id": "wiki_confirm_reset",
            },
        },
    ],
}

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # Get user's information
        user_info = client.users_info(user=event["user"])
        user_name_last = user_info["user"]["profile"]["last_name"]
        user_name_first = user_info["user"]["profile"]["first_name"]
        user_id = user_info["user"]["name"]

        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view = {
                "type": "home",
                "callback_id": "home_view",
                # body of the view
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":wave: Welcome! Jira Wiki Bot"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":white_check_mark: 정책 및 안내"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "-$POLICY INFO$"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":secure: User Status"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*User ID* : {user_id}\n*Username* : {user_name_last}{user_name_first}\n"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Jira 비밀번호 초기화"
                                },
                                "action_id": "Jira_button_clicked"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Wiki 비밀번호 초기화"
                                },
                                "action_id": "Wiki_button_clicked"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Create Jira Webhook"
                                },
                                "action_id": "create_jira_webhook_button"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Edit Jira Webhook"
                                },
                                "action_id": "edit_jira_webhook_button"
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

@app.action("Jira_button_clicked")
def handle_button_1_click(ack, body, client):
    ack()

    # Show the initial modal view with confirmation buttons
    user_id = body["user"]["name"]
    view = jira_initial_password_reset_modal

    response = client.views_open(trigger_id=body["trigger_id"], view=view)
    view_id = response["view"]["id"]

    # Store the view_id associated with the user
    user_view_ids[user_id] = view_id

@app.action("jira_confirm_reset")
def jira_confirm_reset(ack, body, client):
    ack()

    # code for handling confirmation goes here
    user_id = body["user"]["name"]
    #USER_TO_RESET = "testuser"
    USER_TO_RESET = user_id
    JIRA_SERVER = "$YOUR JIRA URL$"
    JIRA_DEV_SERVER = "$YOUR JIRA DEV URL$"
    ADMIN_USERNAME = os.environ['ADMIN_USERNAME']
    ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
    NEW_PASSWORD = os.environ['NEW_PASSWORD']
    API_ENDPOINT = f"{JIRA_SERVER}/rest/api/2/user/password?username={USER_TO_RESET}"
    DEV_API_ENDPOINT = f"{JIRA_DEV_SERVER}/rest/api/2/user/password?username={USER_TO_RESET}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "password": NEW_PASSWORD
    }

    try:
        response = requests.put(API_ENDPOINT, headers=headers, data=json.dumps(payload), auth=(ADMIN_USERNAME, ADMIN_PASSWORD))
        if response.status_code == 204:
            message = "실서버 비밀번호가 $PASSWORD$ 로 초기화되었습니다.\n로그인 후 비밀번호를 변경해서 사용해주세요.\n<https://$YOUR JIRA URL$/secure/ViewProfile.jspa|[비밀번호 변경하기]>"
        else:
            message = f"An error occurred. Response Content:\n{response.content.decode('utf-8')}"
    except Exception as e:
        message = f"An error occurred: {str(e)}"

    try:
        dev_response = requests.put(DEV_API_ENDPOINT, headers=headers, data=json.dumps(payload), auth=(ADMIN_USERNAME, ADMIN_PASSWORD))
        if dev_response.status_code == 204:
            message += f"\n개발서버 비밀번호가 $PASSWORD$ 로 초기화되었습니다.\n로그인 후 비밀번호를 변경해서 사용해주세요.\n<https://$YOUR JIRA DEV URL$/secure/ViewProfile.jspa|[비밀번호 변경하기]>"
        else:
            message = f"An error occurred. Response Content:\n{response.content.decode('utf-8')}"
    except Exception as e:
        message += f"\nAn error occurred on Jira Dev Server: {str(e)}"

    # Create a new modal with the updated message
    updated_view = {
        "type": "modal",
        "callback_id": "password_reset_modal",
        "title": {
            "type": "plain_text",
            "text": "Password Reset",
        },
        "blocks": [
            {
                "type": "section",
                "block_id": "message_block",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
            },
        ],
    }

    # Get the view_id associated with the user
    view_id = user_view_ids.get(user_id)

    if view_id:
        # Update the modal using views_update with the original view_id
        client.views_update(view_id=view_id, view=updated_view)

# Handler for the second button click
@app.action("Wiki_button_clicked")
def handle_button_2_click(ack, body, client):
    ack()

    # Show the initial modal view with confirmation buttons
    user_id = body["user"]["name"]
    view = wiki_initial_password_reset_modal

    response = client.views_open(trigger_id=body["trigger_id"], view=view)
    view_id = response["view"]["id"]

    # Store the view_id associated with the user
    user_view_ids[user_id] = view_id

@app.action("wiki_confirm_reset")
def wiki_confirm_reset(ack, body, client):
    ack()

    user_id = body["user"]["name"]

    # Confluence API endpoint URLs
    confluence_url = "https://$YOUR CONFLUENCE URL$/rpc/xmlrpc"
    confluence_dev_url = "https://$YOUR CONFLUENCE DEV URL$/rpc/xmlrpc"

    # Replace with your Confluence credentials
    username = "$YOUR CREDENTIALS$"
    password = "$YOUR CREDENTIALS$"

    # New password for the user
    new_password = "$PASSWORD$"

    # Initialize message
    message = ""

    # Process for the production server
    try:
        # Create XML-RPC server proxy
        server = xmlrpc.client.ServerProxy(confluence_url, allow_none=True)

        # Authenticate with Confluence and obtain a token
        token = server.confluence2.login(username, password)

        # Change the user's password on the production server
        target_username = user_id
        result = server.confluence2.changeUserPassword(token, target_username, new_password)

        if result:
            message += "비밀번호가 $NEW PASSWORD$ 로 초기화되었습니다.\n로그인 후 비밀번호를 변경해서 사용해주세요.\n<https://$YOUR CONFLUENCE URL$/users/changemypassword.action|[비밀번호 변경하기]>"
        else:
            message += f"Failed to change the password for user '{target_username}' on production server."
    except Exception as e:
        message += f"An error occurred on production server: {str(e)}"

    # Ensure to close the server connection
    server('close')()

    # Process for the development server
    try:
        # Create XML-RPC server proxy
        dev_server = xmlrpc.client.ServerProxy(confluence_dev_url, allow_none=True)

        # Authenticate with Confluence Dev and obtain a token
        dev_token = dev_server.confluence2.login(username, password)

        # Change the user's password on the development server
        dev_result = dev_server.confluence2.changeUserPassword(dev_token, target_username, new_password)

        if dev_result:
            message += "\n개발서버 비밀번호가 $NEW PASSWORD$ 로 초기화되었습니다.\n로그인 후 비밀번호를 변경해서 사용해주세요.\n<https://$YOUR CONFLUENCE DEV URL$/users/changemypassword.action|[비밀번호 변경하기]>"
        else:
            message += f"\nFailed to change the password for user '{target_username}' on development server."
    except Exception as e:
        message += f"\nAn error occurred on development server: {str(e)}"

    # Ensure to close the dev server connection
    dev_server('close')()

    # Create a new modal with the updated message
    updated_view = {
        "type": "modal",
        "callback_id": "password_reset_modal",
        "title": {
            "type": "plain_text",
            "text": "Password Reset",
        },
        "blocks": [
            {
                "type": "section",
                "block_id": "message_block",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
            },
        ],
    }

    # Get the view_id associated with the user
    view_id = user_view_ids.get(user_id)

    if view_id:
        # Update the modal using views_update with the original view_id
        client.views_update(view_id=view_id, view=updated_view)

@app.action("create_jira_webhook_button")
def handle_create_jira_webhook_button_click(ack, body, client):
    ack()  # Acknowledge the button click event immediately
    
    # Define the modal for environment selection
    env_selection_modal = {
        "type": "modal",
        "callback_id": "env_selection_modal",
        "title": {
            "type": "plain_text",
            "text": "Select Environment"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "$YOUR POLICY INFO$",
                }
            },
            {
                "type": "input",
                "block_id": "env_selection_block",
                "element": {
                    "type": "static_select",
                    "action_id": "env_selection",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an environment"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Dev"
                            },
                            "value": "dev"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Prod"
                            },
                            "value": "prod"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Environment"
                }
            }
        ],
        "submit": {
            "type": "plain_text",
            "text": "Next"
        }
    }
    
    # Open the modal for the user to select the environment
    client.views_open(
        trigger_id=body["trigger_id"],
        view=env_selection_modal
    )


@app.view("env_selection_modal")
def handle_environment_selection(ack, body, client, view):
    ack()  # Acknowledge the view submission immediately
    user_id = body["user"]["id"]

    # Retrieve the environment value from the modal
    env = view["state"]["values"]["env_selection_block"]["env_selection"]["selected_option"]["value"]
    
    # Store the selected environment
    user_env_selection[user_id] = env

    # Show the modal for webhook details, conditionally add Dev Jira Key input
    if env == "prod":
        view_to_show = details_modal_prod
    else:
        view_to_show = details_modal  # Use a fresh copy each time to ensure no side-effects
    
    client.views_open(
        trigger_id=body["trigger_id"],
        view=view_to_show
    )

@app.view("webhook_details")
def handle_webhook_details_submission(ack, body, client, view):
    ack()
    user_id = body["user"]["id"]
    user_name = body["user"]["name"]
    values = view["state"]["values"]

    webhook_url = values["webhook_url_input"]["webhook_url"]["value"]
    jql = values["jql_input"]["jql"]["value"]
    dev_jira_key = values.get("dev_jira_key_input", {}).get("dev_jira_key", {}).get("value", "")

    selected_events = [
        option["value"]
        for block_id in ["event_selection_block_1", "event_selection_block_2", "event_selection_block_3", "event_selection_block_4"]
        for option in values[block_id]["event_selection_" + block_id[-1]]["selected_options"]
    ]

    env = user_env_selection.get(user_id, 'prod')  # Default to prod if not found
    jira_url = "https://$YOUR JIRA DEV URL$" if env == "dev" else "https://$YOUR JIRA URL$"
    jira_prod_url = "https://$YOUR JIRA URL$"
    jira_dev_url = "https://$YOUR JIRA DEV URL$"
    jira_today = date.today().isoformat()

    # Check the assignee if environment is 'prod' and Dev Jira Key is provided
    if env == "prod" and dev_jira_key:
        jira_check_url = f"https://$YOUR JIRA URL$/rest/api/2/issue/{dev_jira_key}"

        try:
            response = requests.get(jira_check_url, auth=HTTPBasicAuth('$YOUR CREDENTIALS$', '$YOUR CREDENTIALS$'))
            if response.status_code == 200:
                assignee_username = response.json().get("fields", {}).get("assignee", {}).get("name", "")
                
                if assignee_username != user_name:
                    # If the assignee does not match the Slack user, show an error modal
                    client.views_open(
                        trigger_id=body["trigger_id"],
                        view={
                            "type": "modal",
                            "title": {"type": "plain_text", "text": "Error"},
                            "blocks": [{
                                "type": "section",
                                "text": {"type": "mrkdwn", "text": "입력하신 Jira Key의 assignee가 아닌 것으로 확인됩니다. 올바른 Key를 입력해주세요."}
                            }]
                        }
                    )
                    return
            else:
                # Handle errors with the Jira API response
                client.views_open(
                    trigger_id=body["trigger_id"],
                    view={
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "Error"},
                        "blocks": [{
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": "Jira 이슈가 확인되지 않습니다. 올바른 Key를 입력해주세요."}
                        }]
                    }
                )
                return
        except Exception as e:
            # Handle exceptions during the API call
            client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "modal",
                    "title": {"type": "plain_text", "text": "Error"},
                    "blocks": [{
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"An error occurred: {str(e)}"}
                    }]
                }
            )
            return

    webhook_data = {
        "name": f"{user_name}_{datetime.now().strftime('%Y/%m/%d')}",
        "url": webhook_url,
        "events": selected_events,
        "filters": {"issue-related-events-section": jql} if jql is not None else {},
        "excludeBody": False
    }

    auth = HTTPBasicAuth('$YOUR CREDENTIALS$', '$YOUR CREDENTIALS$')
    response = requests.post(f"{jira_url}/rest/webhooks/1.0/webhook", json=webhook_data, auth=auth)
    modal_text = ""

    if response.status_code == 201:
        modal_text += "Webhook이 성공적으로 등록되었습니다.\n"

        issue_data = {
            "fields": {
                "project": {"key": "SUPPORT"},
                "assignee": {"name": user_name},
                "reporter": {"name": user_name},
                "summary": "Jira Webhook Creation",
                "description": f"Webhook was successfully created by {user_name} on {datetime.now().strftime('%Y/%m/%d')}.\nURL: {webhook_url}\nEvents: {', '.join(selected_events)}\nJQL: {jql}\nenvironment: {env}",
                "issuetype": {
                    "name": "Request(계정/권한/플러그인/지라세팅/Dev API/스페이스생성)"
                },
                "components": [{"id": "60700"}]
            }
        }

        issue_response = requests.post(f"{jira_prod_url}/rest/api/2/issue", json=issue_data, auth=auth)
        if issue_response.status_code == 201:
            issue_key = issue_response.json()['key']
            modal_text += f"https://$YOUR JIRA URL$/browse/{issue_key} 가 생성되었습니다.\nDev 웹훅일 경우 추후 실서버(Prod) 웹훅 생성 시 근거로 필요합니다.\n"

            resolution_data = {
                "update": {"resolution": [{"set": {"name": "Done"}}]},
                "fields": {
                    "customfield_15313": jira_today,
                    "duedate": jira_today,
                    "customfield_15314": jira_today,
                },
                "transition": {"id": "21"}
            }

            update_response = requests.post(f"{jira_prod_url}/rest/api/2/issue/{issue_key}/transitions", json=resolution_data, auth=auth)
            if update_response.status_code == 204:
                modal_text += f"이슈가 Resolved 처리 되었습니다.\n"
            else:
                modal_text += f"이슈 Resolve 실패 {issue_key}. Status code: {update_response.status_code}\n{update_response.text}\n"
                print(f"이슈 Resolve 실패 {issue_key}. Status code: {update_response.status_code}\n{update_response.text}\n")
        else:
            modal_text += f"이슈 생성 실패. Status code: {issue_response.status_code}\n{issue_response.text}\n"
            print(f"이슈 생성 실패. Status code: {issue_response.status_code}\n{issue_response.text}\n")
    else:
        modal_text += f"Webhook 생성에 실패했습니다: {response.status_code} - {response.text}\n"
        print(f"Failed to create webhook: {response.status_code} - {response.text}\n")
        print(f"response: {response}\n")

    display_modal(client, body["trigger_id"], modal_text)

@app.action("edit_jira_webhook_button")
def handle_edit_jira_webhook_button_click(ack, body, client):
    ack()  # Acknowledge the button click event immediately

    # Define the modal for environment selection
    env_selection_modal = {
        "type": "modal",
        "callback_id": "env_edit_selection_modal",
        "title": {
            "type": "plain_text",
            "text": "Select Environment"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "env_edit_selection_block",
                "element": {
                    "type": "static_select",
                    "action_id": "env_edit_selection",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an environment"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Dev"
                            },
                            "value": "dev"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Prod"
                            },
                            "value": "prod"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Environment"
                }
            }
        ],
        "submit": {
            "type": "plain_text",
            "text": "Next"
        }
    }

    # Attempt to open the modal
    client.views_open(trigger_id=body["trigger_id"], view=env_selection_modal)

@app.view("env_edit_selection_modal")
def handle_environment_edit_selection(ack, body, client, view):
    ack()  # Acknowledge the view submission immediately
    user_id = body["user"]["id"]
    user_name = body["user"]["name"]
    

    
    # Retrieve the environment value from the modal
    env = view["state"]["values"]["env_edit_selection_block"]["env_edit_selection"]["selected_option"]["value"]
    # Store the selected environment
    user_env_selection[user_id] = env
    jira_url = "https://$YOUR JIRA DEV URL$/rest/webhooks/1.0/webhook" if env == "dev" else "https://$YOUR JIRA URL$/rest/webhooks/1.0/webhook"
    
    auth = HTTPBasicAuth('$YOUR CREDENTIALS$', '$YOUR CREDENTIALS$')
    
    try:
        # Fetching all webhooks from JIRA
        response = requests.get(jira_url, auth=auth)
        if response.status_code == 200:
            webhooks = response.json()
            # Filter webhooks by lastUpdatedUser matching current Slack user's username
            user_webhooks = [webhook for webhook in webhooks if user_name in webhook['name']]

            # Building blocks for displaying webhooks with checkboxes
            blocks = []
            for webhook in user_webhooks:
                events_list = ', '.join(webhook['events'])  # Assuming 'events' is a list of event names
                jql = webhook['filters'].get('issue-related-events-section', 'No JQL filter set')
                webhook_id = webhook['self'].rsplit('/', 1)[-1]  # Extract the ID from the 'self' URL

                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{webhook['name']}*\nURL: {webhook['url']}\nLast Updated: {datetime.fromtimestamp(webhook['lastUpdated'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}\nEvents: {events_list}\nJQL: {jql}\nID: {webhook_id}"
                    },
                    "accessory": {
                        "type": "button",
                        "text":{
                                "type": "plain_text",
                                "text": "Edit"
                            },
                            "value": webhook_id,
                            "action_id": "handle_edit_button_clicked"
                    }
                })

            edit_webhook_modal = {
                "type": "modal",
                "callback_id": "edit_webhook_modal",
                "title": {"type": "plain_text", "text": "Edit Webhooks"},
                "blocks": blocks
            }

            # Open the modal
            client.views_open(trigger_id=body["trigger_id"], view=edit_webhook_modal)
        else:
            print(f"Failed to fetch webhooks: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


@app.action("handle_edit_button_clicked")
def handle_edit_button_click(ack, body, client):
    ack()  # Acknowledge the button click immediately

    print(body)
    # Extract the webhook_id from the clicked action
    webhook_id = body['actions'][0]['value']
    clicked_block_id = body['actions'][0]['block_id']

    # Initialize webhook_information to None
    webhook_information = None

    # Loop through the blocks to find the one that matches the clicked block_id
    for block in body['view']['blocks']:
        if block['block_id'] == clicked_block_id:
            webhook_information = block['text']['text']
            break
            
    # Here, you can fetch the details of the webhook using webhook_id if needed
    # and prepare the modal to edit the webhook
    edit_webhook_details_modal = {
        "type": "modal",
        "callback_id": "edit_webhook_details",
        "title": {
            "type": "plain_text",
            "text": "Webhook Details"
        },
        "submit": {
            "type": "plain_text",
            "text": "Edit Webhook"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "$YOUR POLICY INFO$",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*-기존 웹훅 정보-*\n" + webhook_information
                }
            },
            {
                "type": "input",
                "block_id": "webhook_url_input",
                "label": {
                    "type": "plain_text",
                    "text": "Webhook URL"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "webhook_url"
                }
            },
            {
                "type": "input",
                "block_id": "jql_input",
                "label": {
                    "type": "plain_text",
                    "text": "JQL Filter"
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "jql"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*$POLICY INFO$*",
                }
            },
            # First group of events - for issues
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_1",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Issues"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_1",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Issue Created"}, "value": "jira:issue_created"},
                        {"text": {"type": "plain_text", "text": "Issue Updated"}, "value": "jira:issue_updated"},
                        {"text": {"type": "plain_text", "text": "Issue Deleted"}, "value": "jira:issue_deleted"},
                        {"text": {"type": "plain_text", "text": "Issue worklog changed"}, "value": "jira:worklog_updated"}
                    ]
                }
            },
            # Second group of events - for worklogs
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_2",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Worklogs"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_2",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Worklog Created"}, "value": "worklog_created"},
                        {"text": {"type": "plain_text", "text": "Worklog Updated"}, "value": "worklog_updated"},
                        {"text": {"type": "plain_text", "text": "Worklog Deleted"}, "value": "worklog_deleted"}
                    ]
                }
            },
            # Third group of events - for comments
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_3",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Comments"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_3",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Comment Added"}, "value": "comment_created"},
                        {"text": {"type": "plain_text", "text": "Comment Edited"}, "value": "comment_updated"},
                        {"text": {"type": "plain_text", "text": "Comment Deleted"}, "value": "comment_deleted"}
                    ]
                }
            },
            # Fourth group of events - for issue links
            {
                "type": "input",
                "optional" : True,
                "block_id": "event_selection_block_4",
                "label": {
                    "type": "plain_text",
                    "text": "Select Events - Issue Links"
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": "event_selection_4",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Issue Link Created"}, "value": "issuelink_created"},
                        {"text": {"type": "plain_text", "text": "Issue Link Deleted"}, "value": "issuelink_deleted"}
                    ]
                }
            }
        ]
    }

    # Open the modal to edit the webhook details
    client.views_push(
        trigger_id=body["trigger_id"],
        view=edit_webhook_details_modal
    )    

@app.view("edit_webhook_details")
def handle_edit_webhook_details_submission(ack, body, client, view):
    ack()
    user_id = body["user"]["id"]
    user_name = body["user"]["name"]
    values = view["state"]["values"]

    webhook_url = values["webhook_url_input"]["webhook_url"]["value"]
    jql = values["jql_input"]["jql"]["value"]
    webhook_id = body["view"]["blocks"][1]["text"]["text"].split("ID: ")[-1]
    
    selected_events = [
        option["value"]
        for block_id in ["event_selection_block_1", "event_selection_block_2", "event_selection_block_3", "event_selection_block_4"]
        for option in values[block_id]["event_selection_" + block_id[-1]]["selected_options"]
    ]

    env = user_env_selection.get(user_id, 'prod')  # Default to prod if not found
    jira_url = "https://$YOUR JIRA DEV URL$" if env == "dev" else "$YOUR JIRA URL$"

    webhook_data = {
        "name": f"{user_name}_{datetime.now().strftime('%Y/%m/%d')}",
        "url": webhook_url,
        "events": selected_events,
        "filters": {"issue-related-events-section": jql} if jql is not None else {},
        "excludeBody": False
    }

    auth = HTTPBasicAuth('$YOUR CREDENTIALS$', '$YOUR CREDENTIALS$')
    response = requests.put(f"{jira_url}/rest/webhooks/1.0/webhook/{webhook_id}", json=webhook_data, auth=auth)
    modal_text = ""

    if response.status_code == 200:
        modal_text += "Webhook이 성공적으로 수정되었습니다.\n"
    else:
        modal_text += f"Webhook 수정에 실패했습니다: {response.status_code} - {response.text}\n"
        print(f"Failed to edit webhook: {response.status_code} - {response.text}\n")
        print(f"response: {response}\n")
    
    # Define the modal content
    modal_content = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Operation Details"},
        "close": {"type": "plain_text", "text": "Close"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": modal_text}
            }
        ]
    }

    print(body)
    client.views_update(
        view_id=body["view"]["previous_view_id"],
        view=modal_content
    )

# Function to display a modal with operation details
def display_modal(client, trigger_id, modal_text):
    # Maximum characters allowed for text in the modal
    max_chars = 2900
    
    # Truncate modal_text if it's longer than max_chars
    if len(modal_text) > max_chars:
        # Optionally, add an ellipsis to indicate the text has been trimmed
        modal_text = modal_text[:max_chars-3] + '...'
    
    # Define the modal content
    modal_content = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Operation Details"},
        "close": {"type": "plain_text", "text": "Close"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": modal_text}
            }
        ]
    }
    
    # Display the modal
    client.views_open(
        trigger_id=trigger_id,
        view=modal_content
    )


def run_bot():
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

run_bot()
  
