const baseUrl="/campaign/api/v1"

function getCampaignIdFromUrl(){
    const path = window.location.pathname
    const parts = path.split("/").filter(Boolean)
    return parts[parts.length - 1]
}

const campaignId = getCampaignIdFromUrl()

const fallbackContentItems = [
    { id:1,title:"مقاله سئو برای فروشگاه",status:"draft"},
    { id:2,title:"راهنمای خرید لپ تاپ",status:"published"},
    { id:3,title:"مقایسه گوشی ها",status:"draft"}
]

window.onload = loadContentItems

async function loadContentItems(){

    try{

        const res = await fetch(
            `/content/api/v1/get-content-items/?campaign_id=${campaignId}`,
            {
                method:"GET",
                credentials:"include"
            }
        )

        const data = await res.json()

        if(data.success){

            let items = []

            data.data.forEach(c=>{
                if(c.items){
                    items = items.concat(c.items)
                }
            })

            renderContentItems(items)

        }else{
            renderContentItems(fallbackContentItems)
        }

    }catch(e){
        renderContentItems(fallbackContentItems)
    }

}

function renderContentItems(items){

    const container = document.getElementById("contentItems")

    container.innerHTML = ""

    container.innerHTML += `
    <div class="content-card add-card" onclick="openCreateModal()">
        +
        <span>افزودن محتوا</span>
    </div>
    `

    items.forEach(i=>{
        container.innerHTML += `
        <div class="content-card">
            <h4>${i.title}</h4>
            <div class="status">وضعیت: ${i.status}</div>
        </div>
        `
    })

}

function openCreateModal(){
    window.location.href = "http://localhost:8000/dashboard/content/create"
}

function closeCreateModal(){
    document.getElementById("createModal").style.display = "none"
}

async function createContentItem(){

    const body = {
        campaign_id: campaignId,
        title: document.getElementById("title").value,
        main_keyword: document.getElementById("keywords").value,
        description: document.getElementById("description").value
    }

    try{

        const res = await fetch(`${baseUrl}/content_item_create`,{
            method:"POST",
            credentials:"include",
            headers:{ "Content-Type":"application/json"},
            body: JSON.stringify(body)
        })

        const data = await res.json()

        if(data.success){
            closeCreateModal()
            loadContentItems()
        }

    }catch(e){
        alert("در حالت دمو محتوا اضافه نشد")
    }

}
