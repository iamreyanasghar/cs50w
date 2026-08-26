document.addEventListener('DOMContentLoaded', function () {


  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  // document.querySelector('#submit').addEventListener('click', send_email);


  // By default, load the inbox
  load_mailbox('inbox');

  const myForm = document.getElementById('compose-form');

  myForm.addEventListener('submit', function (event) {
    event.preventDefault();
    const to = document.getElementById('compose-recipients').value;
    const head = document.getElementById('compose-subject').value;
    const content = document.getElementById('compose-body').value;

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: to,
        subject: head,
        body: content
      })
    })
      .then(response => response.json())
      .then(result => {
        console.log(result);
        load_mailbox('sent')
      });
  })

});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // display appropriate mails
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      // Print emails
      console.log(emails);

      // ... do something else with emails ...

      document.querySelector('#emails-view').innerHTML = emails.map(mail => {
        // 1. Check if the email is read to determine background color
        const backgroundColor = mail.read ? '#e0e0e0' : '#ffffff';

        // 2. Return the structured HTML matching your design
        return `
        <div class="email-box" 
             onclick="viewEmail(${mail.id})" 
             style="display: flex; justify-content: space-between; align-items: center; border: 1px solid black; padding: 10px 15px; margin-bottom: 2px; cursor: pointer; background-color: ${backgroundColor}; font-family: sans-serif; font-size: 20px;">
            
            <!-- Left Side: Sender and Subject -->
            <div style="display: flex; gap: 15px;">
                <span style="font-weight: bold; min-width: 140px;">${mail.sender}</span>
                <span style="color: #000000;">${mail.subject}</span>
            </div>

            <!-- Right Side: Timestamp -->
            <div style="color: #757575;">
                ${mail.timestamp}
            </div>
            
        </div>
    `;
      }).join('');


    });

}

function viewEmail(emailId) {
  // just verify
  console.log("Link worked successfully!")

  // mark it as readed
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })


  // display the email content
}