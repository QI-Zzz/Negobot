function timeout(ms) {
    return new Promise((_, reject) => setTimeout(() => reject(new Error('Request timed out')), ms));
}

class Chatbot{

    constructor(){

        this.args = {
            chat: document.querySelector(".chatbox"),
            sendButton: document.querySelector(".send__button")
        }

        this.wholemessage = [];

        this.requestInProgress = false;
    }

    // const chatbox = document.querySelector(".chatbox");

    display(){
        const {chat, sendButton} = this.args
        const textField = chat.querySelector('input');

        sendButton.addEventListener("click", ()=> {
            if (!this.requestInProgress){
            this.onSendButton(chat)}
        });
        
        

        textField.addEventListener("keydown", (e) => {
            if (!this.requestInProgress && e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
                e.preventDefault();
                this.onSendButton(chat)
            }
        });

    }
 

    onSendButton(chatbot){


        var textField = chatbot.querySelector('input')
        let text1 = textField.value

        if(text1 === ""){
            return
        }

        this.requestInProgress = true;
        // textField.disabled = true;
        // sendButton.disabled = true;

        let user_input = {name: "user", message: text1}
        this.wholemessage.push(user_input);
        // this.updateChatText(chatbot)
        let thinking_input = { name: "bot", message: "Thinking..." };
        this.wholemessage.push(thinking_input);
        this.updateChatText(chatbot);
        textField.value = '';

        Promise.race([
            fetch('/chatbot', {
            
                method: 'POST',
                body: JSON.stringify({message: text1}),
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json'
                },
            }),

            timeout(29000)
        ])

        // fetch('/chatbot', {
            
        //     method: 'POST',
        //     body: JSON.stringify({message: text1}),
        //     mode: 'cors',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        // })
        .then (r => r.json())
        .then (r => {
            this.wholemessage.pop();
            let bot_input = {name: "bot", message: r.answer}
            this.wholemessage.push(bot_input);
 
            this.updateChatText(chatbot)
            // textField.value = ''
            this.requestInProgress = false;


        }).catch((error) => {
            console.error('Error:', error);
            if (error.message === "Request timed out") {
                this.wholemessage.push({name: "bot", message: "Oops! Something went wrong. 😅 Please type it again!"});
            }
            this.updateChatText(chatbot)
            // textField.value = ''
            this.requestInProgress = false;

        }
        )
    }

    


    updateChatText(chatbot){
        var html = '';
        this.wholemessage.slice().reverse().forEach(function(item, index) {
            if (item.name === "bot")
            {
                html += '<div class="messages__item-container">';
                html += '<img class="bot_icon" src="static/bot.svg">';
                html += '<div class="messages__item messages__item--bot">' + item.message + '</div>';
                html += '</div>';
            }
            else
            {
                html += '<div class="messages__item messages__item--user">' + item.message + '</div>'
            }
        });

        const chatmessage = chatbot.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }

    
}

// document.addEventListener("DOMContentLoaded", function() {
const chatbot = new Chatbot();
chatbot.display();
// });

