
async function sendRequest() {
    const method = document.getElementById("method").value;
    const endpoint = document.getElementById("endpoint").value;
    const body = document.getElementById("body").value;

    if (endpoint.length === 0 || endpoint === "/"){
        document.getElementById("response").textContent="Endpoint is required.";
        return;
    }

    else if (method === "POST" && body.length === 0){
        document.getElementById("response").textContent="Body is required for POST method.";
        return;
    }

    else if (method === "DELETE" && !endpoint.includes("/measurements/")) {
        document.getElementById("response").textContent = "DELETE requests require a measurement ID (e.g., /measurements/1)";
        return;
    }

    try {
        const options = {
            method: method,
            headers: {
                "Content-Type": "application/json",
            }
        };
        
        if (method === "POST" || method === "PUT") {
            options.body = body;
        }

        const response = await fetch(endpoint, options);
        const code= response.status;
 
        if((method === "POST" || method === "PUT") && code == 400){
            document.getElementById("response").textContent = "Invalid JSON format in the body.";
            return;
        }

        if(method === "PUT" && code == 405){
            document.getElementById("response").textContent = "Invalid endpoint for PUT method.";
            return;
        }


        const responded = await response.json();
       

        if (code===200) {
            document.getElementById("response").textContent = responded["message"] + " Status: " + code;
            return;
        } 
        if (code===404) {  
            document.getElementById("response").textContent = responded["error"] + " Error Code: " + code;
            return;
        }
        
        document.getElementById("response").textContent = JSON.stringify(responded, null, 2) + " Status Code: " + code;

    } catch (error) {
        document.getElementById("response").textContent = "Invalid endpoint";
    }
}