class Chatbot{

    constructor(){

        this.args = {
            chat: document.querySelector(".chatbox"),
            sendButton: document.querySelector(".send__button")
        }

        this.wholemessage = [];
    }

    // const chatbox = document.querySelector(".chatbox");

    display(){
        const {chat, sendButton} = this.args

        sendButton.addEventListener("click", ()=> this.onSendButton(chat))

        // const node = chat.querySelector('user_input').addEventListener('keypress', ({key}) =>{
        //     if (key.code === 'Enter'){
        //         this.onSendButton(chat)
        //     }
        // })
  
        // node.addEventListener('keydown', ({key}) =>{
        //     if (key.code === 'Enter'){
        //         this.onSendButton(chat)
        //     }
        // })

        // function nameOfYourEventListener(){
        //     document.querySelector("#yourInputID").addEventListener("keydown", function (e){
        //     if (e.code === 'Enter'){
        //         newNote(e); //function that you run for add the content to the list
        //     }});

    }

    onSendButton(chatbot){
        var textField = chatbot.querySelector('input')
        let text1 = textField.value

        if(text1 === ""){
            return
        }

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
                html += '<div class="messages__item-container">';
                html += '<img src="static/bot.svg" width=40px>';
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

