# Learned — continuous log (S.Track → s.AI)

Personal learning log. This file is **user-owned**. Claude does not write here directly — at most, Claude suggests a one-liner the user can paste in.

Capture things you actually understood (not just what got built). Vibe-coded output that you didn't read goes in commit messages, not here.

---

## Format

```
### YYYY-DD-MM — <topic>
- What I learned (in my own words):
- Why it matters / where it applies:
- Open question I still have:
```

---

## Entries

### 2026-24-06 — Postgres
- What I learned (in my own words):
  - Basic postgres syntaxes that translated from ERD diagram in mysqlworkbench. 
  - Applying the postgres onto supabase and creating an initial database
  - Postgres has same logic as normal mysqlworkbench but different syntax so it was quite easy to understand
- Why it matters / where it applies:
  - Learning postgres is required as supabase need them to run.
- Open question I still have:
  - How I would actually implement the logic and create the actual running backend.

  ### 2026-26-06 — Backend stuffs
- What I learned (in my own words):
  - postgres is for supabase but for our backend to understand the database we need to write sql in python 
  - There are many tools in which i haven't fully understand what each of them do yet e.g. uvicorn, and others i forgot.
  - copied some links from supabase to connect with database setup inside backend folder
- Why it matters / where it applies:
  - learning the architectural of the backend and how database and bankend codes are connected, believe this is called SQLAlchemy?
- Open question I still have:
  - everything is confusing right now and i dont have a specific question. Ten, in 6 months, if you understand even 50% of these. I am proud of you.

  ### 2026-27-06 — API endpoints, Pydantic schema, 
  ## API -> SQLAlchemy <- Pydantic schema relations 

- What I learned (in my own words):
  - Writing pydantic schema models, which defines what attribute from the SQLAlchemy is inputted from the frontend.
  - Writing API Endpoints that uses SQLAlchemy models as templates and pydantic as reference to then fill in the other attribute inside SQLAlchemy's table that isn't passed by the frontend using backend logic
- Why it matters / where it applies:
  - Understanding the strucutre will allow me to know what is passed and what needs to be filled
  - API endpoints is one of the main feature in writing backend, gaining deeper understanding of this compounds as I write more endpoints
- Open question I still have:
  - N/A

  ### 2026-27-06 — Auth Wiring

- What I learned (in my own words):
  - Auth wiring by instead of hardcoding ids, create a test user, company, and project inside of supabase.
  - Simulate endpoint with test user id using swagger doc
  - Created command to retreive access key using anon key and user credential do then test endpoints in swagger docs.
- Why it matters / where it applies:
  - Auth wiring is necessary because in development , auth and endpoint testing are required before having a frontend so that we can test out endpoint logics.
- Open question I still have:
  - Still don't know what anon really is. Basically the authorize process is still unclear, why did we need access token? 
  - is what we did manual testing. for example if we have frontend done, when user want to do material request they would need to be authorized using the access key which is generated in the backend automatically. But since we dont have that we need to run command with anon key and user password to generate and input that access key so that we can have access to material request endpoint?
  - Is Auth wiring the idea of generating test user,companies etc. then run endpoints, or is it the process or linking user id with company id inside auth.py so that we can use endpoint with real data?



### 2026-28-06 — Login & Dashboard page (frontend) connection with Supabase auth and GET endpoints (backend)
- What I learned (in my own words):
  - Refresher on react native's html body and that it is similar to next.js. Revision on how to write an async function
  - How to integrate supabase auth so that we can verify frontend's input (credential) against credentials that are stored inside supabase user's row
  - Writing another supabase integration to retrive user's access token and use that in an async function to get their corresponded material request using the GET endpoint we wrote yesterday
  - Started to understand the logic of getting the access token and why it is necessary.
- Why it matters / where it applies:
  - Being able to understand and integrate connections between frontend and backend are skills that are sought for within the industry and make a well rounded engineer
  - Most page in the future will rely on user input to retreive something from the database via using these endpoints
- Open question I still have:
  - No questions just still lost on the general html and javascript syntaxes especially the async functions and the whole writing supabase in the frontend stuff.

  ### 2026-29-06 — Material-Request and Items submission through frontend via POST endpoint
  ## Added PATCH endpoint for owner changing status of material request
- What I learned (in my own words):
  - integrated supabase and endpoint with typescript inside dashboard page for POST material-request endpoint
  - Starting to understand react and typescript syntaxes and usecase e.g. normal function and async function. And different useState syntax e.g. () => ... and that someFunction() runs automatically when opening the page
  - Saw differences in calling endpoint types such as GET calls and set a state whereas POST use JSON.stringify to then pass the object into FASTAPI
  - PATCH is used for changing a current attributes's state of row that already exist inside of the database
- Why it matters / where it applies:
  - Understanding pattern recognition in react and typescript syntax will compound into more efficient coding
  - Understanding the structure between endpoints and frontend
- Open question I still have:
  - N/A

  ### 2026-30-06 — POST Endpoint for purchase order , Splitting current request by status categorically in , Endpoint for deliveries. Caught a BIG DESIGN FLAW
  ## GET endpoints for purchase orders, wired it to frontend through nested react html.
- What I learned (in my own words):
  - Revision for writing POST endpoint for purchasing a requested order
    - body must come before depends arguments
    - db need to add , commit, refresh before able to loop through that added object
  - You could wrap react component inside of a function in typescript then proceed to print them via filtering (Status category)
  - Recognising big design flaw during variance calculation that the previous codebase were going to compare item name in request against ordered. which can create loophole with nameing variations. Changed order_item in supabase, schemas, and pydantics to make order_item reference request_item id so that we have direct link to what is being ticked off in request order
  - Learnt (kinda) and struggled (definitely) through writing purchase-order endpoint since we were wiring many schemas together.  the nested function for printing purchase order and per-item variances. adding conditional styles
- Why it matters / where it applies:
  -  API endpoints and react + typescript tech. useful patterns.
  - Recognising design flaw come from iterating through the system and recognise them while writing the code. just using sonnet without understanding the code would've caught this big flaw later when stages are implemented
- Open question I still have:
  - I am just still unsure about how to handle the other backend stuff like ids and things that arent passed from the frontend and can't be calculated
  - Everything was slowly making sense , but now its back to square one. feeling lost. Gotta keep pushing through.

  ### 2026-01-07 — GET endpoint for purchase-order with order id, Necessary for POST deliveries. Wired them to the frontend. New UI, per-items record states and order dropdown picker for fetching function
- What I learned (in my own words):
  - "|" is used for typescript variable's type annotation while "||" is used during runtime for logical operations
  - in endpoints, if we are passing id through url like /.../{id}/.. we could pass the id directly into the parameter
  - use backtick for urls inside of typescript so that javascript variable can interpolate `${...}`
  - tackled with wiring the endpoint in frontend was a pain. Learnt that during mapping, if out is onChange((e) => ....) which ever mapped index that is clicked return back the value = {...} we assigned into e. Which we then type converges into what we want to pass into the function
  - TypeScipt - useState declaration
    - Set<T> is used for checking existence
    - Record<K,V> is used for dict search
  - Map uses Variable.map((eachItem) => ({...}))   , ({...}) is necessary as it encapsulate and return an object otherwise it will read as function body
  - "Content-Type" : "application/json" tells FASTAPI (endpoint) that we are sending over json object to the endpoint (POST)
- Why it matters / where it applies:
  - these are syntaxes and typescript logics used for writing frontend work
- Open question I still have:
  -

  ### 2026-02-07 — POST delivery photos , Wired to frontend, Tested end-to-end
- What I learned (in my own words):
  - Dealt with reading file in FASTAPI and creating Supabase bucket, which is inserted in the endpoint using f"...." which was new syntaxes
  - File was send in as parameter then await File.read() is used to give byte then sha256 something something turnt it into hash strings
  - File was used as input type in the frontend and the async function utilises FormData() which is new.
  - Encontered access problem with supabase.storage , previously used anon key which cant bypass row level security, need to initialise another supabase_admin variable this time with service_role key to bypass RLS
- Why it matters / where it applies:
  - hashing is done on the server side (fastapi) to prevent fraud of uploading the same byte i.e.
  - RLS access control is important and i need to be able to know what can access what so what should be given control by which variable etc.
  - I should learn reading the terminal instead of copy and pasting error lines into claude. Only last few lines matter so dont get overwhelmed
- Open question I still have:
  - Formdata() purposes and syntax compared to normal type of input are still confusing to me.

- Answers:
FormData(): used when the body contains a file (raw bytes). Regular inputs go as JSON via JSON.stringify with Content-Type: application/json. Files can't fit in JSON, so FormData sends multipart/form-data instead, and the browser sets the Content-Type boundary automatically (which is why you leave that header off in the fetch).

  ### 2026-03-07 — Project Requirement Re-Spec with Manager
- What I learned (in my own words):
  - PO is already generated by another program that the company uses. 
  - Re-spec to a construction material warehousing is more desired my the company
- Why it matters / where it applies:
  - Iterating back and forth with the customer is the way to understand their need and to make a SaaS
- Open question I still have:
  - 

  ### 2026-04-07 — Futher clarifying new project requirement. Finished all SQLAlchemy and Pydantic of v2 spec
- What I learned (in my own words):
  -  a model can self reference itself through foreign key, this is the unary 
  relationship stuff.
  - when to use and not use surrogated id, for example, if  primary key for POLine includes companyID + itemID + PO-ID, this means that that combination can only exist once which may be true but some edge case may involve two different row of the same item
  - alembic is a library that autogenerate postgres from written sqlalchemy, command: alembic revision --autogenerate
  - alembic need to run inside of backend repo and venv activated.
  - Had a refresher on SQLAlchemy and Pydantic schemas, understood more about the overall picture of which field is needed, like oh, companyid and some userid are calculated within the endpoint and not send over in the frontend whereas during v1 schemas, I didnt really understand what get work in which layer
- Why it matters / where it applies:
  - Alembic saves time so that you dont have to write manual postgres then sqlalchem.
  - Modelling exercises help read business requirement into applicable techinical schemas
- Open question I still have:
  - 

### 2026-05-07 — Endpoints for V2 Spec, PHASE A backend endpoints done
- What I learned (in my own words):
  - when entirety of a model is calculated on the server side (endpoint) you can utilise other Post endpoint (receipt) to write stockMovement and stockLevel since it contain all the necessary information
  - juggled three models at the same time in the receipt post endpoint PO fulfilment status. very confusing but once slowed down understand it for 10 seconds until i start writing the code agagain. The whole endpoint had 7 models in used which was mind boggling
- Why it matters / where it applies:
  - juggling logic that requires multiple models are thing that will recur when doing backend work and its one of the important fundamental to get good at
- Open question I still have:


### 2026-06-07 — Wiring to frontends , Created Nav Layout for all pages, Finished dashboard and PO item display
- What I learned (in my own words):
  - Frontend this session leaned heavily into AI assisted writing as I think it would be wiser to focus my time on backend and architecture of backend data rather than shallow frontend syntax
  - Promise.all (typescript) is used before you assign an await to concurrent calls so that they can run alongside each other instead of one after another
  - Type declaring at top of typescript before the function so that inside the useState you can directly specify the type e.g. useState<PurchaseOrder[]>([])
- Why it matters / where it applies:
  - creating explicit type are stricter than using any[] since input type must match the declared at the top
- Open question I still have:

### 2026-07-07 — Frontend wiring (Receive, Stock, Withdraw, Items), Voice to text claude
- What I learned (in my own words):
  - discovered that the concept of frontend for CRUD app such as this is
  similarly the same for all frontend pages. recurring methodlogy fetch database -> input form and storing as states -> create an object and json.stringify via endpoint . as wellas the syntaxes of map and react componenent
  - Voice to text claude 
  - double firing problem inside frontend UI , implmented
  helper function called isSubmitting by awaiting current submission until return
- Why it matters / where it applies:
- Starting to recognise patterns to frontend CRUD syntaxes, compounds
- Voice to text claude allow me to elaborate idea throgugh speaking
which reduces friction compared to typing
- Open question I still have:

### 2026-08-07 — Debugging JWK request. Grilling session with AI
- What I learned (in my own words):
  - All pages contain this bug where the server is still processing the user's token since server need to retrieve the token and parse to endpoint which delays and trigger "Token not exist" therefore a JWKs public key checking is used so that we directly match the token with the public key
  - Voice to text with AI on architectural of system and database design.
- Why it matters / where it applies:
  - Frontend and Backend flow looked perfect but testing end to end will reveal edge cases that you may not be able to think about. Prior to this I have been skipping end to end test and just been writing pages.
  - Today I realised something far more important than this project alone. Anyone can write code , start a business, do ecom. but the most single important question is presentation (speaking). Voice to text input are allowing me to practice that which will be very beneficial in demo displays and job interviews
- Open question I still have:
  - Still dont know what JWKs means and why having a function that checks that with the parameter is more efficient and will solve the problem of not checking in time before the browser load since both are essentially token fetching so I thought they would have the same time complexity
    - ANSWER: supabase.auth.get_user() is a network round trip, while jwt.decode() = local CPU-only math  basically no network latency

### 2026-13-07 — Reading DXF with exdxf
- What I learned (in my own words):
  - Scripts to read dxf using exdxf library and prints them out
  - Wrote another script to read entities , put them in a dictionary then dump that dict into json file inside data
  - 800k lines of json parsed text overwhelming at first
- Why it matters / where it applies:
- Open question I still have:
  - Very confusing, back to dark magic like the start of s.track, but I feel that I am learning which is good.

<!-- Add new entries above this line -->
