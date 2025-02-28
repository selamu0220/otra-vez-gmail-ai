from abacusai import WorkflowGraph, WorkflowGraphNode, WorkflowNodeInputMapping, WorkflowNodeInputType, WorkflowNodeInputSchema

# Authentication Module
def gmail_authentication_function(oauth_trigger: object):
    """
    📧 Gmail Login
    
    This function helps you connect to your Gmail account.
    Steps:
    1. Click the authentication button
    2. Log in to your Gmail account
    3. Give permission to the app
    """
    from abacusai import AgentResponse, ApiClient
    try:
        client = ApiClient()
        connector = client.get_connector_auth(service='GMAILUSER')
        auth_info = connector.auth
        if auth_info and auth_info.get('accessToken'):
            return AgentResponse(
                status='success', 
                info='✅ Successfully connected to Gmail! You can now send emails.'
            )
        else:
            return AgentResponse(
                status='error', 
                info='❌ Gmail connection failed. Please click the button to connect to Gmail.'
            )
    except Exception as e:
        return AgentResponse(
            status='error', 
            info=f'❌ Error connecting to Gmail: {str(e)}'
        )

# Email Creation Module
def draft_email_function(email_instructions: object):
    """
    ✍️ Email Writer
    
    This function helps you write professional emails.
    Features:
    1. Remembers your contacts
    2. Creates professional email content
    3. Suggests subject lines
    
    Just describe what you want to write!
    """
    from abacusai import AgentResponse, ApiClient
    import re
    client = ApiClient()
    
    # First, check Gmail connection
    try:
        auth = client.get_connector_auth(service='GMAILUSER')
        if not auth or not auth.auth.get('accessToken'):
            return AgentResponse(
                recipient_email='', 
                email_subject='', 
                draft_email='', 
                error='📝 Please connect to Gmail first by clicking the authentication button above.'
            )
    except Exception as e:
        return AgentResponse(
            recipient_email='', 
            email_subject='', 
            draft_email='', 
            error=f'❌ Gmail connection error: {str(e)}'
        )
    
    client.stream_message('✍️ Creating your email...')
    
    # Look for contact name
    name_extraction_prompt = f'''
    Extract any person's name from the following text, or return 'NONE' if no name is mentioned:
    {email_instructions}
    Reply with just the name or 'NONE'.
    '''
    name_response = client.evaluate_prompt(
        prompt=name_extraction_prompt,
        system_message="Extract only the name of the person mentioned, or reply 'NONE' if no name is found.",
        temperature=0.0
    )
    extracted_name = name_response.content.strip()
    
    # Check address book
    stored_email = None
    if extracted_name != 'NONE':
        history = client.get_agent_context_chat_history()
        for msg in history:
            if msg.role == 'ASSISTANT' and 'STORED_CONTACT' in msg.text:
                stored_contact_match = re.search(f'{extracted_name}:([^,]+)', msg.text)
                if stored_contact_match:
                    stored_email = stored_contact_match.group(1).strip()
                    break
    
    # Create email content
    prompt = f'''
    Based on the following instructions, create a professional email.
    Instructions: {email_instructions}

    {f"📗 Found in address book: {extracted_name}: {stored_email}" if stored_email else ""}

    Format your response as follows:
    RECIPIENT: {stored_email if stored_email else '[email address]'}
    SUBJECT: [subject line]
    CONTENT:
    [email content]

    If this is a new contact, add a note starting with "STORE_CONTACT:" with the name and email.
    '''
    
    response = client.evaluate_prompt(
        prompt=prompt,
        system_message='You are a professional email assistant. Create well-written emails.',
        max_tokens=800
    )
    
    # Process the email
    content = response.content
    recipient = 'TO BE FILLED'
    subject = ''
    email_body = ''
    store_contact = None
    
    for line in content.split('\n'):
        if line.startswith('RECIPIENT:'):
            recipient = line.replace('RECIPIENT:', '').strip()
        elif line.startswith('SUBJECT:'):
            subject = line.replace('SUBJECT:', '').strip()
        elif line.startswith('STORE_CONTACT:'):
            store_contact = line.replace('STORE_CONTACT:', '').strip()
        elif line.startswith('CONTENT:'):
            email_body = '\n'.join(content.split('\n')[content.split('\n').index(line) + 1:]).strip()
    
    if store_contact:
        client.stream_message(f'📗 Added to address book: {store_contact}')
    
    return AgentResponse(
        recipient_email=recipient,
        email_subject=subject,
        draft_email=email_body
    )

# Email Sending Module
def send_email_function(recipient_email: object, email_subject: object, draft_email: object):
    """
    📤 Email Sender
    
    This function sends your email through Gmail.
    Steps:
    1. Reviews the email details
    2. Sends through your Gmail account
    3. Confirms when sent
    """
    from abacusai import AgentResponse, ApiClient
    import base64
    from email.mime.text import MIMEText
    import requests
    
    client = ApiClient()
    try:
        # Get Gmail connection
        auth = client.get_connector_auth(service='GMAILUSER')
        access_token = auth.auth['accessToken']
        
        # Prepare email
        message = MIMEText(draft_email)
        message['to'] = recipient_email
        message['subject'] = email_subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send email
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            headers=headers,
            json={'raw': raw}
        )
        
        if response.status_code == 200:
            return AgentResponse(
                success='true',
                message=f'✅ Email sent successfully to {recipient_email}'
            )
        else:
            return AgentResponse(
                success='false',
                message=f'❌ Failed to send email: {response.text}'
            )
    except Exception as e:
        return AgentResponse(
            success='false',
            message=f'❌ Error sending email: {str(e)}'
        )

# Create workflow nodes with clear organization
gmail_auth_node = WorkflowGraphNode(
    name="Gmail Authentication",
    function=gmail_authentication_function,
    input_mappings=[
        WorkflowNodeInputMapping(
            name="oauth_trigger",
            variable_type=WorkflowNodeInputType.USER_INPUT,
            is_required=True
        )
    ],
    input_schema=WorkflowNodeInputSchema(
        json_schema={
            "type": "object",
            "title": "📧 Connect to Gmail",
            "required": ["oauth_trigger"],
            "properties": {
                "oauth_trigger": {
                    "type": "string",
                    "title": "Connect Gmail",
                    "description": "Click here to connect your Gmail account"
                }
            }
        }
    ),
    output_mappings=["status", "info"]
)

draft_email_node = WorkflowGraphNode(
    name="Draft Email",
    function=draft_email_function,
    input_mappings=[
        WorkflowNodeInputMapping(
            name="email_instructions",
            variable_type=WorkflowNodeInputType.USER_INPUT,
            is_required=True
        )
    ],
    input_schema=WorkflowNodeInputSchema(
        json_schema={
            "type": "object",
            "title": "✍️ Write Email",
            "required": ["email_instructions"],
            "properties": {
                "email_instructions": {
                    "type": "string",
                    "title": "Email Instructions",
                    "description": "Describe the email you want to write"
                }
            }
        },
        ui_schema={
            "email_instructions": {
                "ui:widget": "textarea"
            }
        }
    ),
    output_mappings=["recipient_email", "email_subject", "draft_email", "error"]
)

send_email_node = WorkflowGraphNode(
    name="Send Email",
    function=send_email_function,
    input_mappings=[
        WorkflowNodeInputMapping(
            name="recipient_email",
            variable_type=WorkflowNodeInputType.WORKFLOW_VARIABLE,
            variable_source="Draft Email"
        ),
        WorkflowNodeInputMapping(
            name="email_subject",
            variable_type=WorkflowNodeInputType.WORKFLOW_VARIABLE,
            variable_source="Draft Email"
        ),
        WorkflowNodeInputMapping(
            name="draft_email",
            variable_type=WorkflowNodeInputType.WORKFLOW_VARIABLE,
            variable_source="Draft Email"
        )
    ],
    output_mappings=["success", "message"]
)

# Create the workflow graph
workflow_graph = WorkflowGraph(
    nodes=[gmail_auth_node, draft_email_node, send_email_node],
    primary_start_node="Gmail Authentication"
)

# Update the agent with the new organized structure
client.update_agent(
    model_id="954bcfff4",
    workflow_graph=workflow_graph,
    description="""📧 Email Assistant - Simple Email Manager

📁 Organized in Three Simple Modules:

1. 📧 Gmail Connection
   - Connects to your Gmail account
   - Keeps your connection secure
   - One-time setup

2. ✍️ Email Writer
   - Helps write professional emails
   - Remembers your contacts
   - Creates well-written content
   - Suggests good subject lines

3. 📤 Email Sender
   - Reviews email details
   - Sends through Gmail
   - Confirms delivery

💡 How to Use:
1. Click "Connect Gmail" button
2. Tell it what email to write
3. Review and send!

📗 Features:
- Saves your contacts
- Professional writing
- Easy to use
- Secure Gmail connection

Note: You'll need to connect your Gmail account first time you use this.""",
    user_level_connectors={
        "GMAILUSER": ["https://www.googleapis.com/auth/gmail.modify"]
    },
    ui_config={
        "theme": {
            "primaryColor": "#1a73e8",
            "secondaryColor": "#4285f4",
            "backgroundColor": "#f8f9fa"
        },
        "header": {
            "title": "Gmail Assistant",
            "subtitle": "Tu asistente personal para correos electrónicos",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg"
        },
        "widgets": {
            "sidebar": True,
            "welcomeMessage": "¡Bienvenido a tu asistente de Gmail! Comienza conectando tu cuenta.",
            "showSteps": True
        }
    }
)