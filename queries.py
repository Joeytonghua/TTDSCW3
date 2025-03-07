# QUERIES = {
#     "general": [
#         '("breaking news" OR "top stories" OR "latest updates")',
#         '("world events" OR "trending topics" OR "global news")',
#         '("social issues" OR "public opinion" OR "society trends")',
#         '("elections" OR "political debates" OR "government policies")',
#         '("natural disasters" OR "earthquakes" OR "hurricanes")',
#         '("human rights" OR "freedom of speech" OR "activism")',
#         '("crime rates" OR "police investigations" OR "justice system")',
#         '("education reforms" OR "school policies" OR "college admissions")',
#         '("climate crisis" OR "environmental issues" OR "sustainability")'
#     ],
#     "world": [
#         '("international relations" OR "global conflicts" OR "foreign affairs")',
#         '("United Nations" OR "G7 Summit" OR "NATO")',
#         '("war zones" OR "military alliances" OR "geopolitical tensions")',
#         '("trade agreements" OR "sanctions" OR "economic policies")',
#         '("refugee crisis" OR "migration policies" OR "border security")',
#         '("global pandemics" OR "epidemic outbreaks" OR "public health")',
#         '("energy crisis" OR "oil prices" OR "renewable energy policies")',
#         '("humanitarian aid" OR "poverty reduction" OR "international aid")',
#         '("diplomatic relations" OR "treaties" OR "embassy affairs")'
#     ],
#     "nation": [
#         '("national security" OR "counterterrorism" OR "homeland defense")',
#         '("presidential elections" OR "parliament decisions" OR "congress bills")',
#         '("public protests" OR "civil movements" OR "social justice")',
#         '("economic growth" OR "inflation rates" OR "GDP changes")',
#         '("healthcare policies" OR "public health system" OR "medical reforms")',
#         '("criminal justice" OR "law enforcement" OR "court rulings")',
#         '("infrastructure projects" OR "urban development" OR "transportation systems")',
#         '("education funding" OR "university admissions" OR "school reforms")',
#         '("military strategies" OR "defense spending" OR "armed forces")'
#     ],
#     "business": [
#         '("stock market" OR "NASDAQ" OR "Dow Jones")',
#         '("cryptocurrency" OR "Bitcoin" OR "Ethereum")',
#         '("startup funding" OR "venture capital" OR "Silicon Valley")',
#         '("corporate mergers" OR "acquisitions" OR "business expansion")',
#         '("real estate market" OR "housing trends" OR "mortgage rates")',
#         '("global trade" OR "supply chain" OR "logistics crisis")',
#         '("e-commerce" OR "retail industry" OR "online shopping trends")',
#         '("digital banking" OR "fintech revolution" OR "mobile payments")',
#         '("oil prices" OR "energy markets" OR "commodities trading")'
#     ],
#     "technology": [
#         '("artificial intelligence" OR "machine learning" OR "deep learning")',
#         '("blockchain technology" OR "cryptography" OR "decentralization")',
#         '("cybersecurity threats" OR "data breaches" OR "hacking incidents")',
#         '("cloud computing" OR "big data analytics" OR "distributed systems")',
#         '("quantum computing" OR "supercomputers" OR "high-performance computing")',
#         '("5G networks" OR "wireless technology" OR "next-gen communications")',
#         '("autonomous vehicles" OR "self-driving cars" OR "transportation AI")',
#         '("virtual reality" OR "augmented reality" OR "metaverse development")',
#         '("space exploration" OR "NASA missions" OR "commercial space travel")'
#     ],
#     "entertainment": [
#         '("Hollywood movies" OR "blockbuster films" OR "cinema industry")',
#         '("Netflix series" OR "streaming platforms" OR "digital entertainment")',
#         '("K-pop music" OR "BTS" OR "global pop culture")',
#         '("celebrity news" OR "famous actors" OR "music artists")',
#         '("music festivals" OR "live concerts" OR "global tours")',
#         '("video game industry" OR "esports tournaments" OR "gaming trends")',
#         '("Bollywood films" OR "Indian cinema" OR "Asian entertainment")',
#         '("Oscar awards" OR "Academy Awards" OR "Golden Globes")',
#         '("comic book adaptations" OR "Marvel Universe" OR "DC Comics")'
#     ],
#     "sports": [
#         '("FIFA World Cup" OR "UEFA Champions League" OR "Premier League")',
#         '("NBA basketball" OR "MVP race" OR "playoffs results")',
#         '("Olympics gold medals" OR "athletics world records" OR "international sports")',
#         '("Formula 1 racing" OR "Grand Prix" OR "motor sports")',
#         '("Wimbledon tennis" OR "US Open" OR "Grand Slam champions")',
#         '("Super Bowl" OR "NFL championship" OR "American football")',
#         '("cricket world cup" OR "T20 league" OR "international cricket")',
#         '("cycling championships" OR "Tour de France" OR "mountain biking")',
#         '("combat sports" OR "boxing world titles" OR "UFC fights")'
#     ],
#     "science": [
#         '("space exploration" OR "NASA research" OR "Mars missions")',
#         '("black holes" OR "dark matter" OR "cosmic expansion")',
#         '("climate change impact" OR "global warming solutions" OR "carbon neutrality")',
#         '("biotechnology advancements" OR "genetic engineering" OR "CRISPR")',
#         '("particle physics" OR "Large Hadron Collider" OR "subatomic particles")',
#         '("oceanography" OR "marine biology" OR "deep sea discoveries")',
#         '("renewable energy innovations" OR "solar power" OR "wind energy")',
#         '("synthetic biology" OR "lab-grown meat" OR "bioengineered foods")',
#         '("neuroscience breakthroughs" OR "brain-computer interface" OR "cognitive studies")'
#     ],
#     "health": [
#         '("COVID-19 updates" OR "global pandemics" OR "public health crisis")',
#         '("mental health awareness" OR "depression treatment" OR "anxiety management")',
#         '("cancer research breakthroughs" OR "immunotherapy" OR "oncology studies")',
#         '("vaccination programs" OR "herd immunity" OR "public health policies")',
#         '("telemedicine expansion" OR "AI in healthcare" OR "digital hospitals")',
#         '("opioid epidemic" OR "drug addiction treatments" OR "rehabilitation programs")',
#         '("nutrition science" OR "healthy diets" OR "obesity prevention")',
#         '("infectious disease control" OR "WHO guidelines" OR "pandemic response")',
#         '("Alzheimer\'s disease research" OR "neurodegenerative disorders" OR "brain health")'
#     ]
# }
QUERIES = {
    "general": [
        "(breaking OR headlines OR trending OR latest OR news)",
        "(society OR community OR public OR welfare OR crisis)",
        "(government OR policy OR election OR democracy OR reform)",
        "(disaster OR emergency OR earthquake OR flood OR hurricane)",
        "(justice OR crime OR law OR police OR court)",
        "(education OR university OR school OR students OR learning)"
    ],
    "world": [
        "(international OR global OR foreign OR diplomacy OR relations)",
        "(war OR military OR conflict OR peace OR crisis)",
        "(sanctions OR trade OR economy OR exports OR imports)",
        "(refugees OR migration OR immigration OR border OR crisis)",
        "(diplomacy OR United Nations OR NATO OR agreements)"
    ],
    "nation": [
        "(security OR defense OR military OR homeland OR borders)",
        "(president OR congress OR parliament OR lawmakers OR government)",
        "(economy OR inflation OR GDP OR growth OR crisis)",
        "(crime OR violence OR homicide OR corruption OR police)",
        "(education OR universities OR reforms OR policies OR students)",
        "(healthcare OR hospital OR insurance OR medical OR patients)"
    ],
    "business": [
        "(stocks OR finance OR banking OR investment OR Wall Street)",
        "(cryptocurrency OR Bitcoin OR blockchain OR Ethereum OR digital)",
        "(startup OR venture OR capital OR funding OR entrepreneurship)",
        "(e-commerce OR retail OR sales OR shopping OR consumers)",
        "(real estate OR housing OR property OR mortgage OR rent)",
        "(trade OR economy OR exports OR imports OR globalization)"
    ],
    "technology": [
        "(AI OR artificial OR intelligence OR machine OR learning)",
        "(cybersecurity OR hacking OR breach OR malware OR phishing)",
        "(cloud OR computing OR data OR servers OR storage)",
        "(blockchain OR cryptocurrency OR Bitcoin OR Ethereum OR NFT)",
        "(robotics OR automation OR drones OR self-driving OR autonomous)",
        "(VR OR AR OR virtual OR augmented OR reality)"
    ],
    "entertainment": [
        "(Hollywood OR movies OR films OR actors OR cinema)",
        "(Netflix OR streaming OR series OR TV OR shows)",
        "(music OR concerts OR bands OR pop OR rock)",
        "(video OR gaming OR esports OR PlayStation OR Xbox)",
        "(Bollywood OR celebrities OR singers OR producers OR directors)",
        "(fashion OR trends OR lifestyle OR awards OR influencers)"
    ],
    "sports": [
        "(FIFA OR football OR soccer OR World Cup OR UEFA)",
        "(NBA OR basketball OR playoffs OR finals OR MVP)",
        "(Olympics OR athletes OR gold OR world OR champion)",
        "(Formula 1 OR motorsport OR Grand Prix OR racing OR cars)",
        "(Tennis OR Wimbledon OR Open OR Grand Slam OR Federer)",
        "(boxing OR UFC OR MMA OR heavyweight OR championship)"
    ],
    "science": [
        "(space OR NASA OR Mars OR rocket OR satellite)",
        "(physics OR quantum OR energy OR matter OR universe)",
        "(climate OR environment OR warming OR carbon OR pollution)",
        "(biology OR genetics OR DNA OR evolution OR medicine)",
        "(ocean OR marine OR sea OR deep OR exploration)",
        "(chemistry OR elements OR reactions OR periodic OR atoms)"
    ],
    "health": [
        "(COVID OR virus OR pandemic OR outbreak OR flu)",
        "(mental OR health OR stress OR depression OR anxiety)",
        "(cancer OR disease OR therapy OR treatment OR drugs)",
        "(nutrition OR fitness OR diet OR weight OR exercise)",
        "(vaccination OR immune OR prevention OR medicine OR doctors)",
        "(hospitals OR healthcare OR surgery OR medical OR diagnosis)"
    ]
}
