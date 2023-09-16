class Chatbot{

    constructor(){

        this.args = {
            chat: document.querySelector(".chatbox"),
            sendButton: document.querySelector(".send__button")
        }

        this.wholemessage = [];
    }

    display(){
        const {chat, sendButton} = this.args

        sendButton.addEventListener("click", ()=> this.onSendButton(chat))

        // const node = chat.querySelector('user_input');
        // node.addEventListener('keyup', ({key}) =>{
        //     if (key === 'Enter'){
        //         this.onSendButton(chat)
        //     }
        // })

    }

    onSendButton(chatbot){
        var textField = chatbot.querySelector('input')
        let text1 = textField.value

        if(text1 === ""){
            return
        }

        let user_input = {name: "user", message: text1}
        this.wholemessage.push(user_input);

        fetch('http://127.0.0.1:5000/chatbot', {
            
            method: 'POST',
            body: JSON.stringify({message: text1}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then (r => r.json())
        .then (r => {
            let bot_input = {name: "bot", message: r.answer}
            this.wholemessage.push(bot_input);
            this.updateChatText(chatbot)
            textField.value = ''
        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbot)
            textField.value = ''
        }
        )
    }    

    updateChatText(chatbot){
        var html = '';
        this.wholemessage.slice().reverse().forEach(function(item, index) {
            if (item.name === "bot")
            {
                html += '<div class="messages__item messages__item--bot">' + item.message + '</div>'
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

