const messages = document.getElementById("messages")
const input = document.getElementById("chatInput")
const sendBtn = document.getElementById("sendBtn")
const suggestions = document.querySelectorAll(".suggestion-pill")

/* ------------------ csrf ------------------ */

function getCookie(name) {
let cookieValue = null
if (document.cookie && document.cookie !== "") {
const cookies = document.cookie.split(";")
for (let i = 0; i < cookies.length; i++) {
const cookie = cookies[i].trim()
if (cookie.substring(0, name.length + 1) === (name + "=")) {
cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
break
}
}
}
return cookieValue
}

const csrftoken = getCookie("csrftoken")


/* ------------------ ui helpers ------------------ */

function addMessage(text, type) {

const row = document.createElement("div")
row.className = "msg-row " + type

const bubble = document.createElement("div")
bubble.className = "msg-bubble " + (type === "user" ? "msg-user" : "msg-bot")
bubble.innerText = text

row.appendChild(bubble)
messages.appendChild(row)

messages.scrollTop = messages.scrollHeight
}

function typingIndicator() {

const row = document.createElement("div")
row.className = "msg-row bot"

const bubble = document.createElement("div")
bubble.className = "msg-bubble msg-bot typing"
bubble.innerHTML = "<span></span><span></span><span></span>"

row.appendChild(bubble)
messages.appendChild(row)

messages.scrollTop = messages.scrollHeight

return row
}


/* ------------------ chat send ------------------ */

async function send() {

const text = input.value.trim()
if (!text) return

addMessage(text, "user")
input.value = ""

const typing = typingIndicator()

try {

const res = await fetch("/api/chat/", {
method: "POST",
headers: {
"Content-Type": "application/json",
"X-CSRFToken": csrftoken
},
body: JSON.stringify({
message: text
})
})

const data = await res.json()

typing.remove()

addMessage(data.reply, "bot")

} catch (e) {

typing.remove()
addMessage("خطا در ارتباط با سرور.", "bot")

}

}

sendBtn.onclick = send

input.addEventListener("keydown", e => {
if (e.key === "Enter") send()
})


/* ------------------ suggestions ------------------ */

suggestions.forEach(el => {

el.onclick = () => {

input.value = el.innerText
el.classList.add("used")
send()

}

})


/* ------------------ theme ------------------ */

const toggle = document.getElementById("themeToggle")

toggle.onclick = () => {

const root = document.documentElement
const current = root.getAttribute("data-theme")

if (current === "dark") {

root.removeAttribute("data-theme")
localStorage.theme = "light"

} else {

root.setAttribute("data-theme", "dark")
localStorage.theme = "dark"

}

}

if (localStorage.theme === "dark") {
document.documentElement.setAttribute("data-theme", "dark")
}


/* ------------------ scroll progress ------------------ */

const progress = document.getElementById("scrollProgress")

window.addEventListener("scroll", () => {

const h = document.documentElement
const sc = (h.scrollTop) / (h.scrollHeight - h.clientHeight) * 100
progress.style.width = sc + "%"

})


/* ------------------ footer year ------------------ */

document.getElementById("year").innerText = new Date().getFullYear()


/* ------------------ toast ------------------ */

function toast(text) {

const t = document.getElementById("toast")
t.innerText = text
t.classList.add("show")

setTimeout(() => t.classList.remove("show"), 2500)

}
