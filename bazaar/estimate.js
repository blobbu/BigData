
var arr = []
var i = 4;
var tmp;
while(true){
    try{
        tmp = document.querySelector(`body > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(${i}) > td:nth-child(4)`).textContent
    } catch(error){
        tmp = null
    }
    
    if (!tmp){
        break;
    }
    while(tmp.charAt(0) === ' '){
        tmp = tmp.substring(1);
        }

    arr.push(tmp); 
    i = i+1
}
var sum=0;
for (var i = 0; i < arr.length; i++){
    if (arr[i].endsWith('K')){
        num = arr[i].slice(0, -1);
        sum = sum + num*1024;
    } else if (arr[i].endsWith('M')){
        num = arr[i].slice(0, -1);
        sum = sum + num*1024*1024;
    } else if (arr[i].endsWith('G')){
        num = arr[i].slice(0, -1);
        sum = sum + num*1024*1024*1024;
    } 
}

console.log(Math.round(sum/1024/1024/1024) + " GB")
//wyszło ~80GB wszystkiego a nie wszystko to exe