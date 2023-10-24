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

        fetch('/chatbot', {
            
            method: 'POST',
            body: JSON.stringify({message: text1}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then (r => r.json())
        .then (r => {
            this.wholemessage.pop();
            let bot_input = {name: "bot", message: r.answer}
            this.wholemessage.push(bot_input);
            // this.requestInProgress = false;
            // textField.disabled = false;
            // sendButton.disabled = false;
            this.updateChatText(chatbot)
            textField.value = ''
            this.requestInProgress = false;
            // textField.disabled = false;
            // sendButton.disabled = false;

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbot)
            textField.value = ''
            this.requestInProgress = false;
            // textField.disabled = false;
            // sendButton.disabled = false;

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




    // const createChatLi = (message, className) => {
    //     // Create a chat <li> element with passed message and className
    //     const chatLi = document.createElement("li");
    //     chatLi.classList.add("chat", ${className});
    //     let chatContent = className === "outgoing" ? <p></p> : <span class="material-symbols-outlined">smart_toy</span><p></p>;
    //     chatLi.innerHTML = chatContent;
    //     chatLi.querySelector("p").textContent = message;
    //     return chatLi; // return chat <li> element
    // }
    
}

// document.addEventListener("DOMContentLoaded", function() {
const chatbot = new Chatbot();
chatbot.display();
// });

