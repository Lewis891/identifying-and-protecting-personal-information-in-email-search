
function highlight(){
    const features = JSON.parse(document.getElementById('feature_list').textContent)
    const topics = JSON.parse(document.getElementById('topics_list').textContent)
    let content = document.getElementById('result').innerHTML
    document.getElementById('result').innerHTML = transformContent(content, features, topics)
}

function transformContent(content, keywords, topic_words){
  let temp = content

  keywords.forEach(keyword => {
    temp = temp.replace(new RegExp(keyword, 'ig'), wrapKeywordWithHTML(keyword))
  })

  topic_words.forEach(keyword => {
    temp = temp.replace(new RegExp(keyword, 'ig'), wrapwordWithHTML(keyword))
  })

  return temp
}

function wrapKeywordWithHTML(keyword){
  return `<span style="color: #8FFF00">${keyword}</span>`
}

function wrapwordWithHTML(keyword){
  return `<span style="color: #43A6C6">${keyword}</span>`
}

function unHighlight(){
    const body = JSON.parse(document.getElementById('body').textContent)
    document.getElementById('result').innerHTML = body
}