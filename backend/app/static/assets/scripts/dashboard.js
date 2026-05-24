/* =====================================
   CANVAS UTILS
===================================== */

function prepareCanvas(canvas){

const rect = canvas.getBoundingClientRect()

canvas.width = rect.width
canvas.height = rect.height

return {
ctx: canvas.getContext("2d"),
w: canvas.width,
h: canvas.height
}

}


/* =====================================
   LINE CHART
===================================== */

function drawLineChart(canvas,data){

const {ctx,w,h} = prepareCanvas(canvas)

const padding = 30

ctx.clearRect(0,0,w,h)

/* GRID */

ctx.strokeStyle = "rgba(255,255,255,0.06)"
ctx.lineWidth = 1

for(let i=0;i<5;i++){

const y = padding + (h-padding*2)/4*i

ctx.beginPath()
ctx.moveTo(padding,y)
ctx.lineTo(w-padding,y)
ctx.stroke()

}

/* LINE */

ctx.beginPath()

ctx.strokeStyle="#00e5ff"
ctx.lineWidth=3

data.forEach((v,i)=>{

const x = padding + i*((w-padding*2)/(data.length-1))
const y = h-padding-(v/100)*(h-padding*2)

if(i===0) ctx.moveTo(x,y)
else ctx.lineTo(x,y)

})

ctx.stroke()

/* POINTS */

data.forEach((v,i)=>{

const x = padding + i*((w-padding*2)/(data.length-1))
const y = h-padding-(v/100)*(h-padding*2)

ctx.beginPath()
ctx.arc(x,y,4,0,Math.PI*2)
ctx.fillStyle="#ffffff"
ctx.fill()

})

}


/* =====================================
   BAR CHART
===================================== */

function drawBarChart(canvas,data){

const {ctx,w,h} = prepareCanvas(canvas)

ctx.clearRect(0,0,w,h)

const barWidth = w/(data.length*2)

data.forEach((v,i)=>{

const barHeight = (v/100)*h

const x = i*barWidth*2 + barWidth
const y = h-barHeight

ctx.fillStyle="#00b7ff"

ctx.fillRect(
x,
y,
barWidth,
barHeight
)

})

}


/* =====================================
   PIE CHART
===================================== */

function drawPieChart(canvas,data,colors){

const {ctx,w,h} = prepareCanvas(canvas)

ctx.clearRect(0,0,w,h)

const radius = Math.min(w,h)/2-10

const total = data.reduce((a,b)=>a+b,0)

let start = 0

data.forEach((v,i)=>{

const angle = (v/total)*(Math.PI*2)

ctx.beginPath()

ctx.moveTo(w/2,h/2)

ctx.arc(
w/2,
h/2,
radius,
start,
start+angle
)

ctx.closePath()

ctx.fillStyle = colors[i]

ctx.fill()

start += angle

})

}


/* =====================================
   DONUT CHART
===================================== */

function drawDonutChart(canvas,data,colors){

drawPieChart(canvas,data,colors)

const ctx = canvas.getContext("2d")

const w = canvas.width
const h = canvas.height

ctx.beginPath()

ctx.arc(
w/2,
h/2,
Math.min(w,h)/4,
0,
Math.PI*2
)

ctx.fillStyle = "#0f172a"

ctx.fill()

}


/* =====================================
   INIT DASHBOARD CHARTS
===================================== */

document.addEventListener("DOMContentLoaded",()=>{

const trend = document.getElementById("contentTrend")
const platform = document.getElementById("platformChart")
const weekly = document.getElementById("weeklyChart")
const keyword = document.getElementById("keywordGrowth")
const status = document.getElementById("contentStatus")

if(trend)
drawLineChart(
trend,
[20,40,35,60,80,70,95]
)

if(keyword)
drawLineChart(
keyword,
[10,20,35,50,55,70,85]
)

if(weekly)
drawBarChart(
weekly,
[30,45,20,60,75,50]
)

if(platform)
drawPieChart(
platform,
[45,35,20],
[
"#00e5ff",
"#0077ff",
"#00c896"
]
)

if(status)
drawDonutChart(
status,
[60,25,15],
[
"#00eaff",
"#ffaa00",
"#ff4d6d"
]
)

})


/* =====================================
   CHATBOT TOGGLE
===================================== */

document.getElementById("chatbotBtn")?.addEventListener("click",()=>{

const panel = document.getElementById("chatbotPanel")

if(panel) panel.style.display="flex"

})

document.getElementById("closeChatbot")?.addEventListener("click",()=>{

const panel = document.getElementById("chatbotPanel")

if(panel) panel.style.display="none"

})
