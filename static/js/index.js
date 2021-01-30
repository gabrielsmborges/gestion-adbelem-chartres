var date = new Date()

document.getElementById("create-date").min = date.toISOString().split("T")[0];
document.getElementById("create-date").value = date.toISOString().split("T")[0];
document.getElementById("create-hour").value = date.toLocaleTimeString().substr(0, 5)
console.log(date.toLocaleTimeString().substr(0, 5))