# Welcome to cusmo ! The simplest metrics gathering web platform :D


<h3>
            <p>
                Endpoints :
                <ul>
                    <li><i>/hit/&lt;endpoint&gt;?custom_param1=...&custom_param2=...</i> The url you want to hit to store the request. The all additional parameters will be stored in database as dictionnary and available in json stats in 'custom_data':{} key of each request.</li>
                    <li><i>/endpoint_stats/&lt;endpoint&gt;?api_key=...</i> The url to retirieve metrics a full database of requests on the endpoint in json format</li>
                </ul>
            </p>

            <p>
                Exemple of use :
                <br>
                If you want to know how much people are using your program, you just need to generate an endpoint, and make a get request to it at startup.
                Same if you want to know how much people are using a specific feature, you just make a request to a generated endpoint each time someone is using it.
            </p>

                <h4>Javascript exemple:</h4><br>
                <code>
                    function store_visit(){<br>
                        
                        var x = new XMLHttpRequest();<br>
                        x.onload = function() {<br>
                            var resp = JSON.parse(x.responseText);<br>
                            
                        }<br>
                        x.open("GET","http://thaaoblues.pythonanywhere.com/hit/&lt;endpoint_id&gt;",true);<br>                        
                        x.setRequestHeader('X-Referer', window.location.href);<br>
                        x.send();<br>
                    }<br>
                </code>

</h3>
