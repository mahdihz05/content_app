const baseUrl="/campaign/api/v1"

let selectedGoal=null
let selectedPlatform=null
let schemaFields=[]
let dynamicSelections={}

const fallbackGoals=[
{id:1,name:"Brand Awareness"},
{id:2,name:"Traffic"},
{id:3,name:"Lead Generation"},
{id:4,name:"Sales"}
]

const fallbackPlatforms=[
{id:1,name:"Website"},
{id:2,name:"Twitter"},
{id:3,name:"LinkedIn"},
{id:4,name:"Instagram"}
]

window.onload=async function(){
    await loadGoals()
    await loadPlatforms()
}

async function loadGoals(){
    try{
        const res=await fetch(`${baseUrl}/get_goal_list`)
        const data=await res.json()
        renderCards(data.data || [],"goal")
    }catch(e){
        renderCards(fallbackGoals,"goal")
    }
}

async function loadPlatforms(){
    try{
        const res=await fetch(`/platform/api/v1/get_platforms`)
        const data=await res.json()
        renderCards(data.data || [],"platform")
    }catch(e){
        renderCards(fallbackPlatforms,"platform")
    }
}

function renderCards(data,type){
    const grid=document.getElementById(type==="goal"?"goalGrid":"platformGrid")
    grid.innerHTML=""

    data.forEach(item=>{
        const card=document.createElement("div")
        card.className="select-card"
        card.innerText=(type==="goal" ? item.short_description || item.goal || item.name : item.name)

        card.onclick=()=>{
            grid.querySelectorAll(".select-card").forEach(c=>c.classList.remove("active"))
            card.classList.add("active")

            if(type==="goal") selectedGoal=item.id
            if(type==="platform") selectedPlatform=item.id
        }

        grid.appendChild(card)
    })
}

async function loadSchema(){
    const title=document.getElementById("title").value.trim()
    const keyword=document.getElementById("main_keyword").value.trim()

    if(!title || !keyword){
        alert("عنوان و کلمه کلیدی الزامی است")
        return
    }

    if(!selectedGoal){
        alert("هدف کمپین را انتخاب کنید")
        return
    }

    try{
        const res=await fetch(`${baseUrl}/get_goal_schema?goal_id=${selectedGoal}`)
        const data=await res.json()

        if(data.success && data.data){
            const schema=data.data.schema
            schemaFields=schema.fields || []
        }else{
            throw new Error()
        }
    }catch(e){
        schemaFields=[
            {name:"page_title",label:"Page Title",type:"text"},
            {name:"main_keywords",label:"Main Keywords",type:"text"},
            {name:"description",label:"Description",type:"textarea"}
        ]
    }

    renderForm(schemaFields)

    document.getElementById("step1").style.display="none"
    document.getElementById("step2").style.display="block"

    document.getElementById("step-indicator-1").classList.remove("active")
    document.getElementById("step-indicator-2").classList.add("active")
}

function renderForm(fields){
    const container=document.getElementById("dynamicForm")
    container.innerHTML=""

    fields.forEach(field=>{
        let input=""

        if(field.type==="text"){ input=`<input id="${field.name}" type="text">` }
        else if(field.type==="textarea"){ input=`<textarea id="${field.name}"></textarea>` }
        else if(field.type==="number"){ input=`<input id="${field.name}" type="number">` }
        else if(field.type==="url"){ input=`<input id="${field.name}" type="url">` }
        else if(field.type==="select"){
            let cards=""
            field.options.forEach(opt=>{
                cards+=`
                    <div class="select-card dynamic-card"
                    onclick="selectDynamicOption('${field.name}','${opt}',this)">
                    ${opt}
                    </div>
                `
            })
            input=`<div id="dynamic-${field.name}" class="card-grid">${cards}</div>`
        }

        container.innerHTML+=`
        <div class="form-group">
            <label>${field.label || field.name}</label>
            ${input}
        </div>
        `
    })
}

function selectDynamicOption(fieldName,value,element){
    const container=document.getElementById(`dynamic-${fieldName}`)
    container.querySelectorAll(".select-card").forEach(c=>c.classList.remove("active"))
    element.classList.add("active")
    dynamicSelections[fieldName]=value
}

async function createCampaign(){
    const title=document.getElementById("title").value.trim()
    const keyword=document.getElementById("main_keyword").value.trim()

    if(!title || !keyword){
        alert("عنوان و کلمه کلیدی الزامی است")
        return
    }

    if(!selectedGoal){
        alert("هدف کمپین انتخاب نشده")
        return
    }

    const body={
        title:title,
        main_keyword:keyword,
        goal:selectedGoal,
        description:"",
        tag:"product",
        status:"draft",
        settings:{}
    }

    if(selectedPlatform){
        body.platform=selectedPlatform
    }

    schemaFields.forEach(f=>{
        if(f.type==="select"){
            if(dynamicSelections[f.name]){
                body.settings[f.name]=dynamicSelections[f.name]
            }
        }else{
            const el=document.getElementById(f.name)
            if(el && el.value){ body.settings[f.name]=el.value }
        }
    })

    try{
        const res=await fetch(`${baseUrl}/create_campaign`,{
            method:"POST",
            credentials:"include",
            headers:{ "Content-Type":"application/json" },
            body:JSON.stringify(body)
        })

        const data=await res.json()
        const box=document.getElementById("resultBox")

        if(data.success){
            box.innerHTML="<span style='color:var(--success-color)'>کمپین با موفقیت ایجاد شد</span>"
            setTimeout(()=>{ window.location.href="/dashboard/campaign-list" },1200)
        }else{
            box.innerHTML=`<span style='color:var(--error-color)'>${data.error || "خطا در ایجاد کمپین"}</span>`
        }

    }catch(err){
        document.getElementById("resultBox").innerHTML=
        "<span style='color:var(--error-color)'>خطا در ارتباط با سرور</span>"
    }
}
