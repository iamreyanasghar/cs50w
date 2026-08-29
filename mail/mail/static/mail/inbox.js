document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archive').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

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
        load_mailbox('sent');
      });
  });
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#read-email').style.display = 'none';
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
  document.querySelector('#read-email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // display appropriate mails
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      console.log(emails);

      document.querySelector('#emails-view').innerHTML += emails.map(mail => {
        const backgroundColor = mail.read ? '#e0e0e0' : '#ffffff';

        // Fixed: Wrapped '${mailbox}' in single quotes so it passes as a string in HTML
        return `
        <div class="email-box" 
             onclick="viewEmail(${mail.id}, '${mailbox}')" 
             style="display: flex; justify-content: space-between; align-items: center; border: 1px solid black; padding: 10px 15px; margin-bottom: 2px; cursor: pointer; background-color: ${backgroundColor}; font-family: sans-serif; font-size: 20px;">
            
            <div style="display: flex; gap: 15px;">
                <span style="font-weight: bold; min-width: 140px;">${mail.sender}</span>
                <span style="color: #000000;">${mail.subject}</span>
            </div>

            <div style="color: #757575;">
                ${mail.timestamp}
            </div>
        </div>
        `;
      }).join('');
    });
}

function viewEmail(emailId, mailbox) {
  // Fixed: Chained a .then() block to ensure read status saves before displaying the email
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({ read: true })
  })
    .then(() => {
      // display the email content
      fetch(`/emails/${emailId}`)
        .then(response => response.json())
        .then(email => {
          console.log(email);

          document.querySelector('#emails-view').style.display = 'none';
          document.querySelector('#compose-view').style.display = 'none';
          document.querySelector("#read-email").style.display = 'block';

          const id = email.id;
          const sender = email.sender;
          const subject = email.subject;
          const body = email.body;
          const time = email.timestamp;
          const receiver = email.recipients;
          const archived = email.archived;

          document.querySelector("#read-email").innerHTML = `
          <p> <b>From:</b> ${sender} </p>
          <p> <b>To:</b> ${receiver} </p>
          <p> <b>Subject:</b> ${subject} </p>
          <p> <b>Timestamp:</b> ${time} </p>
          <button id="reply-btn">Reply</button>
          ${(mailbox !== 'sent') ? `<button id="archive-btn">${archived ? 'Unarchive' : 'Archive'}</button>` : ''}
          <hr>
          <p>${body}</p>
        `;

          // Fixed: Using addeventlisteners instead of inline onclick functions avoids global scoping issues
          document.querySelector('#reply-btn').addEventListener('click', () => replyMail(id));
          if (mailbox !== 'sent') {
            document.querySelector('#archive-btn').addEventListener('click', () => archiveMail(id, archived));
          }
        });
    });
}

function replyMail(mailId) {
  fetch(`/emails/${mailId}`)
    .then(response => response.json())
    .then(email => {
      const receiver = email.sender;
      const time = email.timestamp;

      const subject = email.subject.startsWith('Re: ') ? email.subject : `Re: ${email.subject}`;

      // Fixed: Appended the old text body to the response note instead of wiping it
      const body = `\n\nOn ${time} ${receiver} wrote:\n${email.body}`;

      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'block';
      document.querySelector("#read-email").style.display = 'none';

      document.querySelector('#compose-recipients').value = receiver;
      document.querySelector('#compose-subject').value = subject;
      document.querySelector('#compose-body').value = body;
    });
}

// Fixed: Simplified parameters to pass the target action directly to the API
function archiveMail(mailId, currentArchiveState) {
  fetch(`/emails/${mailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !currentArchiveState
    })
  })
    .then(() => {
      // Fixed: Now accurately reloads the inbox only *after* the API registers the update
      load_mailbox('inbox');
    });
}