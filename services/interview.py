import requests
import json
import re

def generate_local_questions(matched_skills, missing_skills):
    questions = []
    tech_skill = matched_skills[0] if matched_skills else "Software Engineering"
    miss_skill = missing_skills[0] if missing_skills else "Docker/Kubernetes"
    
    # 1. Technical
    questions.append({
        "type": "Technical", "difficulty": "Medium",
        "question": f"Can you describe your experience with {tech_skill} architecture and scaling applications?",
        "ideal_answer": f"In my previous roles, I used {tech_skill} to build modular, clean systems. I ensured scalability by employing microservices, optimizing database queries, and setting up Redis cache layers to improve response times.",
        "key_points": [f"Explain core concepts of {tech_skill}", "Mention caching, caching layers, and database optimization", "Demonstrate scaling metrics"],
        "follow_up_questions": [f"How do you handle threading or async tasks in {tech_skill}?", "What is the biggest pitfall of {tech_skill} at scale?"],
        "star_answer": {
            "situation": f"We needed to scale our database throughput which relied heavily on {tech_skill}.",
            "task": "My task was to decrease load times and implement microservices architecture.",
            "action": "I refactored the core services and added async task queues.",
            "result": "Response times decreased by 40% and CPU utilization dropped by 20%."
        },
        "short_answer": f"I design scalable applications in {tech_skill} by optimizing queries, caching data, and keeping services decoupled.",
        "detailed_answer": f"Scaling {tech_skill} applications requires identifying bottleneck nodes. First, analyze query execution plans. Next, introduce caching layers like Redis for heavy read operations. Additionally, implement horizontal scaling and asynchronous task processing using Celery or RabbitMQ to execute CPU-intensive processes out-of-band.",
        "common_mistakes": ["Focusing only on code syntax rather than system architecture", "Failing to mention caching and horizontal scaling"],
        "confidence_tips": "Speak clearly about specific bottleneck metrics. Use terms like 'throughput', 'latency', and 'concurrency' with conviction."
    })
    
    # 2. Behavioral
    questions.append({
        "type": "Behavioral", "difficulty": "Medium",
        "question": "Describe a time you led a team through a complex project under tight deadlines.",
        "ideal_answer": "In my last project, we faced a sudden client launch deadline. I broke the project down into critical deliverables, delegated items using Agile boards, organized daily standups, and focused on unblocking team members, allowing us to deliver 2 days early.",
        "key_points": ["Agile planning", "Task delegation", "Communication and unblocking team members"],
        "follow_up_questions": ["How did you handle conflict within the team?", "What would you do differently if faced with the same deadline?"],
        "star_answer": {
            "situation": "Our main API gateway failed right before a critical product launch.",
            "task": "I had to coordinate a team of 4 engineers to rebuild the gateway under a 24-hour deadline.",
            "action": "I set up a war room, split tasks based on expertise, and managed external communications.",
            "result": "We redeployed the gateway with 4 hours to spare, achieving 99.9% uptime."
        },
        "short_answer": "I handle tight deadlines by planning clearly, delegating based on strengths, and running quick daily standups.",
        "detailed_answer": "Faced with tight deadlines, I start by defining the MVP. I map dependencies using an Agile board and hold daily syncs. I ensure there is constant communication between frontend and backend engineers, and I act as a buffer against scope creep from product management.",
        "common_mistakes": ["Saying 'I did it all myself' instead of highlighting team collaboration", "Not quantifying the outcome"],
        "confidence_tips": "Use the 'We' structure for effort but 'I' structure for leadership decisions. Maintain strong eye contact."
    })
    
    # 3. Role-Specific
    questions.append({
        "type": "Role Specific", "difficulty": "Hard",
        "question": f"How do you approach modernizing legacy systems using {miss_skill}?",
        "ideal_answer": f"Modernizing with {miss_skill} involves containerizing services, defining clear infrastructure-as-code configuration, establishing CI/CD pipelines, and gradually routing traffic to the containerized environment using canary deployments.",
        "key_points": ["Containerization principles", "CI/CD integration", "Canary or Blue-Green deployment strategies"],
        "follow_up_questions": [f"What security practices do you use in {miss_skill} configurations?", f"How do you monitor container health in {miss_skill}?"],
        "star_answer": {
            "situation": "The deployment process for our legacy monolith was slow and manual.",
            "task": "My task was to containerize the app using modern build structures.",
            "action": "I wrote clean Dockerfiles, optimized image sizes, and set up GitHub Actions.",
            "result": "Deployment times went from 45 minutes to under 5 minutes with zero downtime."
        },
        "short_answer": "I containerize legacy apps to improve environment consistency and automate deployments using CI/CD pipelines.",
        "detailed_answer": "Modernizing legacy apps involves decomposing dependencies. First, create lightweight images by choosing alpine base images. Second, map configuration settings to environment variables. Third, deploy containers into orchestrated clusters with automated scaling policies.",
        "common_mistakes": ["Using bloated container base images", "Hardcoding configuration secrets in the Dockerfile"],
        "confidence_tips": "Explain the differences between dev and prod configurations. Speak with structured, step-by-step clarity."
    })
    
    # 4. HR
    questions.append({
        "type": "HR", "difficulty": "Easy",
        "question": "Why do you want to join our organization and what makes you a good fit?",
        "ideal_answer": "I have been following your growth and technical innovations. My experience matches your tech stack perfectly, and I thrive in collaborative team environments where I can build impactful user-centric products.",
        "key_points": ["Aligning company values", "Stating technical overlap", "Focusing on collaboration"],
        "follow_up_questions": ["Where do you see yourself in 5 years?", "What are your salary expectations?"],
        "star_answer": {
            "situation": "I was looking for a role that combined my passion for AI and scale.",
            "task": "I researched companies leading this space and found your optimization portal.",
            "action": "I matched my background in spaCy and Flask to your job description requirements.",
            "result": "I am here today prepared to explain how I can immediately add value to your team."
        },
        "short_answer": "I want to leverage my backend experience to build scale and join a company with a high-growth tech culture.",
        "detailed_answer": "I want to join because your team is solving complex scalability challenges. My background in building clean APIs, implementing ML matchers, and optimizing database pipelines directly matches the requirements. I am excited to collaborate with a team that values clean architecture.",
        "common_mistakes": ["Giving a generic answer without mentioning the company's specific product or mission", "Focusing too much on what the company can do for you rather than what you bring to the table"],
        "confidence_tips": "Smile and show genuine enthusiasm. Speak about the company's achievements with interest."
    })

    # 5. Technical
    questions.append({
        "type": "Technical", "difficulty": "Hard",
        "question": "How do you handle database concurrency and prevent race conditions in high-traffic APIs?",
        "ideal_answer": "Database concurrency is managed using isolation levels, pessimistic locking (e.g. SELECT FOR UPDATE), or optimistic locking with version columns. Distributed locks via Redis can also prevent concurrency conflicts at the application tier.",
        "key_points": ["Optimistic vs Pessimistic locking", "Transaction isolation levels", "Distributed locking"],
        "follow_up_questions": ["What is a deadlock and how do you resolve it?", "When would you choose optimistic locking over pessimistic?"],
        "star_answer": {
            "situation": "Our booking API suffered double-booking race conditions during flash sales.",
            "task": "I had to guarantee absolute inventory consistency under concurrent requests.",
            "action": "I implemented optimistic concurrency control and configured database index constraints.",
            "result": "Race conditions fell to absolute zero, protecting transaction integrity."
        },
        "short_answer": "I resolve concurrency conflicts using optimistic locking, strict database constraints, and Redis-based distributed locks.",
        "detailed_answer": "To prevent race conditions, analyze the write contention. For low contention, optimistic locking with a version integer is ideal. For high contention, pessimistic locking secures the row during transaction execution. Additionally, using unique index constraints ensures database level integrity.",
        "common_mistakes": ["Handling locking only in application memory instead of at the database level", "Configuring overly strict isolation levels that cause massive deadlock cascades"],
        "confidence_tips": "Explain the trade-offs of performance vs consistency. Use terms like ACID, isolation levels, and lock escalation."
    })

    # 6. Behavioral
    questions.append({
        "type": "Behavioral", "difficulty": "Medium",
        "question": "Can you describe a time you had a technical disagreement with a team member and how you resolved it?",
        "ideal_answer": "When resolving technical conflicts, I focus on facts, data, and testing. I set up a quick POC for both solutions to compare throughput, query times, and code complexity, allowing the team to choose objectively.",
        "key_points": ["Active listening", "POC comparisons", "Data-driven decision making"],
        "follow_up_questions": ["What would you do if the conflict remained unresolved?", "How do you handle disagreement from senior stakeholders?"],
        "star_answer": {
            "situation": "A team member wanted NoSQL while I proposed SQL for our relational ledger data.",
            "task": "We needed to align on the database architecture within 3 days.",
            "action": "I set up benchmark queries showing SQL outperformed on relational joins by 5x.",
            "result": "The team aligned on the SQL architecture, leading to robust data consistency."
        },
        "short_answer": "I resolve technical conflicts by creating quick POC benchmarks to evaluate performance and align on data.",
        "detailed_answer": "I approach technical disagreements with empathy and objectivity. I write down the pros and cons of both designs. Then, I suggest a time-boxed spike to gather concrete performance data. This takes emotion out of the equation and aligns the team around metrics.",
        "common_mistakes": ["Becoming defensive or taking technical feedback personally", "Escalating conflicts to management immediately without attempting technical alignment"],
        "confidence_tips": "Express respect for different design patterns. Highlight collaboration and team alignment."
    })

    # 7. Role-Specific
    questions.append({
        "type": "Role Specific", "difficulty": "Medium",
        "question": "How do you secure API endpoints against common OWASP Top 10 vulnerabilities?",
        "ideal_answer": "Securing API endpoints requires input validation, parameterized queries to prevent SQLi, rate limiting to stop DDoS, JWT signature checks, and proper CORS settings.",
        "key_points": ["SQL injection prevention", "Rate limiting and throttling", "JWT verification and CSRF protections"],
        "follow_up_questions": ["What is CORS and why is it important?", "How do you protect REST endpoints from brute force attacks?"],
        "star_answer": {
            "situation": "Our legacy endpoints suffered payload injections and lack of rate limits.",
            "task": "My task was to audit and secure our entire backend API catalog.",
            "action": "I implemented validator decorators, parameterized all raw queries, and configured rate-limiting middleware.",
            "result": "Vulnerabilities dropped to zero on security scans, blocking malicious requests."
        },
        "short_answer": "I protect endpoints using input validation, token verification, strict CORS configurations, and rate-limiting rules.",
        "detailed_answer": "OWASP threats are mitigated systematically. Prevent SQLi by using ORMs or parameterized queries. Secure authentication using signed JWT tokens with short expirations. Block brute-force attacks via rate-limiters at the API Gateway level (e.g. Nginx or Kong).",
        "common_mistakes": ["Storing secret tokens in frontend client code", "Failing to check request payload sizes before processing"],
        "confidence_tips": "Enumerate specific measures (e.g., sanitization, encryption). Speak about security as a continuous lifecycle process."
    })

    # 8. HR
    questions.append({
        "type": "HR", "difficulty": "Medium",
        "question": "Where do you see yourself professionally in the next five years?",
        "ideal_answer": "Over the next five years, I want to deepen my skills in backend architecture, take on mentoring roles, and lead larger system designs that drive substantial business outcomes.",
        "key_points": ["Deepening technical skills", "Leadership growth", "Long-term commitment to company goals"],
        "follow_up_questions": ["What specific technologies do you want to learn next?", "How do you plan to develop your leadership capabilities?"],
        "star_answer": {
            "situation": "I wanted to define a clear roadmap for my growth as a staff engineer.",
            "task": "My task was to balance technical contributions with leadership experience.",
            "action": "I set milestones for system architecture design and peer mentoring.",
            "result": "I am looking for a company where I can execute this roadmap and deliver quality code."
        },
        "short_answer": "I see myself taking on leadership roles in backend architecture and mentoring junior developers.",
        "detailed_answer": "In five years, I plan to transition from a senior developer to a principal architect. I want to lead major infrastructural designs and establish coding standards. Additionally, I look forward to mentoring other engineers and collaborating with product teams to build scale.",
        "common_mistakes": ["Giving a generic response that lacks ambition", "Expressing plans that don't align with the role or company"],
        "confidence_tips": "Demonstrate passion for engineering. Frame your growth as a benefit to the engineering team."
    })

    # 9. Technical
    questions.append({
        "type": "Technical", "difficulty": "Medium",
        "question": "What is the difference between REST, GraphQL, and gRPC architectures and when would you use each?",
        "ideal_answer": "REST is simple and standard for public APIs. GraphQL minimizes payload overhead by letting clients query specific fields. gRPC is high-performance, using HTTP/2 and Protocol Buffers, making it ideal for internal microservices.",
        "key_points": ["REST CRUD simplicity", "GraphQL request flexibility", "gRPC Protocol Buffers performance"],
        "follow_up_questions": ["What is HTTP/2 and how does gRPC leverage it?", "What is under-fetching and over-fetching?"],
        "star_answer": {
            "situation": "Our internal microservice REST endpoints suffered high serialization latency.",
            "task": "We needed to refactor communications to support higher concurrency.",
            "action": "I migrated internal communications to gRPC with binary serialization.",
            "result": "Latency fell by 60% and CPU utilization on microservices dropped by 15%."
        },
        "short_answer": "I use REST for public routes, GraphQL for client-heavy interfaces, and gRPC for high-performance microservices.",
        "detailed_answer": "REST is standard for most CRUD operations. GraphQL is ideal when client pages need flexible data queries without round-trips. gRPC is superior for server-to-server microservices due to its low serialization overhead, multiplexing support, and strong type safety using protobufs.",
        "common_mistakes": ["Using GraphQL for simple APIs where it adds unnecessary schema complexity", "Exposing raw gRPC endpoints directly to standard web clients without a proxy"],
        "confidence_tips": "Contrast serialization methods (JSON vs Protobuf). Explain specific use cases clearly."
    })

    # 10. Behavioral
    questions.append({
        "type": "Behavioral", "difficulty": "Hard",
        "question": "Tell me about a major production outage you were involved in and how you handled it.",
        "ideal_answer": "During outages, my priority is communication and restoration. I analyze logs, rollback the last deploy if it caused the bug, isolate the failure node, and coordinate with the team to deploy a hotfix.",
        "key_points": ["Calm coordination", "Root cause analysis", "Post-mortem prevention"],
        "follow_up_questions": ["How did you prevent the outage from recurring?", "How did you communicate with stakeholders during the event?"],
        "star_answer": {
            "situation": "Our payment gateway crashed during black Friday due to deadlocks.",
            "task": "I had to restore service while protecting transaction ledger records.",
            "action": "I scaled the replica pool, routed traffic to static retry queues, and patched the database lock.",
            "result": "Outage was resolved in 14 minutes, saving thousands in potential transaction losses."
        },
        "short_answer": "I handle outages by isolating the failure node, rolling back changes if needed, and documenting a post-mortem.",
        "detailed_answer": "During an outage, I immediately join the incident call. I check error rates in Datadog or ELK. If the issue started right after a release, I execute a safe rollback. Once resolved, I lead a post-mortem to set up alerts and unit test coverage to prevent recurrences.",
        "common_mistakes": ["Blaming other team members for the crash", "Failing to explain the preventive actions taken after the outage"],
        "confidence_tips": "Focus on the recovery process. Show resilience, leadership, and a focus on operational stability."
    })

    # 11. Role-Specific
    questions.append({
        "type": "Role Specific", "difficulty": "Medium",
        "question": "How do you design a CI/CD pipeline to automate testing and zero-downtime deployment?",
        "ideal_answer": "CI/CD pipelines automate testing and deployment using tools like GitHub Actions. Zero-downtime is achieved via blue-green deployments, rolling updates, or canary releases.",
        "key_points": ["Automated test suites", "Zero downtime strategies (Blue-Green)", "Infrastructure as Code"],
        "follow_up_questions": ["What is a rollback trigger in a pipeline?", "How do you handle migrations during zero-downtime deploys?"],
        "star_answer": {
            "situation": "Our legacy deployments were manual and caused 5 minutes of downtime each release.",
            "task": "My task was to automate deployments and guarantee zero downtime.",
            "action": "I configured GitHub Actions and set up rolling updates on our container cluster.",
            "result": "Deployments became fully automated, executing in under 3 minutes with zero user impact."
        },
        "short_answer": "I automate deploys using CI/CD pipelines (e.g. GitHub Actions) and rolling container updates to prevent user downtime.",
        "detailed_answer": "A robust CI/CD pipeline runs unit tests on every commit, builds lightweight docker images, and runs integration tests. For deployment, we use Kubernetes rolling updates to replace old pods gradually, ensuring traffic is only routed to healthy containers.",
        "common_mistakes": ["Failing to automate rollbacks on deployment health checks", "Exposing API keys in pipeline code repositories"],
        "confidence_tips": "Outline step-by-step pipeline phases: Build, Test, Release, Monitor. Speak with operational confidence."
    })

    # 12. HR
    questions.append({
        "type": "HR", "difficulty": "Medium",
        "question": "What are your salary expectations for this position?",
        "ideal_answer": "I am open to market-rate packages that align with my senior experience in python backend engineering. I look forward to reviewing the comprehensive compensation structure including benefits.",
        "key_points": ["Focusing on total compensation", "Setting reasonable market ranges", "Keeping negotiation open"],
        "follow_up_questions": ["What is your current compensation?", "Are you open to equity options?"],
        "star_answer": {
            "situation": "I needed to address compensation expectations without locking myself in too early.",
            "task": "My task was to share a professional range based on market research.",
            "action": "I researched average compensation for senior Python engineers in similar hubs.",
            "result": "I am confident we can reach a mutually beneficial agreement once we align on the role details."
        },
        "short_answer": "I expect a competitive package in line with my backend architecture background and market standards.",
        "detailed_answer": "Based on my research and experience building scalable backend microservices, I am looking for a package in the range of $110,000 to $130,000. However, I am highly interested in the overall opportunity and am open to discussing the full compensation plan.",
        "common_mistakes": ["Giving a single hard number too early without research", "Appearing rigid or refusing to discuss total benefits packages"],
        "confidence_tips": "Deliver your range calmly. Position the discussion around the mutual value you bring to the engineering organization."
    })

    # 13. Technical
    questions.append({
        "type": "Technical", "difficulty": "Medium",
        "question": "How do you use Redis or caching layers to improve API performance and reduce database load?",
        "ideal_answer": "Caching stores database query results in-memory. We use cache-aside patterns to check Redis first, returning cached data, and querying the database only on cache misses, write-through writes update both.",
        "key_points": ["Cache aside strategy", "Cache invalidation strategies", "Handling Cache stampede"],
        "follow_up_questions": ["What is TTL and how do you choose it?", "How do you prevent cache stampede?"],
        "star_answer": {
            "situation": "Our reporting API database was overloaded with identical read queries.",
            "task": "I had to reduce database query load by caching common static calculations.",
            "action": "I implemented Redis cache-aside with a 5-minute TTL invalidation strategy.",
            "result": "Database load dropped by 80% and API response times fell from 800ms to 45ms."
        },
        "short_answer": "I cache static or heavy read query results in Redis, utilizing appropriate TTL settings to ensure freshness.",
        "detailed_answer": "I implement Redis using the cache-aside pattern. For high-traffic nodes, set a reasonable Time-To-Live (TTL) to balance data freshness and database protection. For updates, invalidate the cache immediately. I handle stampedes by using mutex locks or pre-calculating keys.",
        "common_mistakes": ["Caching highly dynamic data without an invalidation policy", "Not handling cache connection failures gracefully in code"],
        "confidence_tips": "Discuss cache stampede and TTL invalidation. Speak about scaling read operations."
    })

    # 14. Behavioral
    questions.append({
        "type": "Behavioral", "difficulty": "Medium",
        "question": "How do you explain complex technical concepts to non-technical stakeholders?",
        "ideal_answer": "I use analogies, visual diagrams, and focus on the business impact (e.g. cost savings, load time reductions) rather than technical details like lines of code or database settings.",
        "key_points": ["Using analogies", "Focusing on business outcomes", "Avoiding jargon"],
        "follow_up_questions": ["How do you handle stakeholders who demand technical details?", "Can you give an example of an analogy you've used?"],
        "star_answer": {
            "situation": "I needed to explain why migrating to microservices was worth a 2-month engineering investment.",
            "task": "I had to get sign-off from the product manager who cared about user features.",
            "action": "I compared monolithic code to a single highway where a crash stops all traffic, and microservices to bypass roads.",
            "result": "The PM approved the migration, which later prevented two major launch day outages."
        },
        "short_answer": "I explain tech issues by using analogies and focusing on how it affects the user experience and business outcomes.",
        "detailed_answer": "When presenting to stakeholders, I avoid engineering jargon. I focus on key metrics: speed, cost, and reliability. I use diagrams and describe the system in terms of real-world workflows. This helps bridge the gap between engineering decisions and business priorities.",
        "common_mistakes": ["Using acronyms or details that confuse the audience", "Over-simplifying to the point of being patronizing"],
        "confidence_tips": "Speak clearly and check for understanding. Focus on the value the change brings to the product."
    })

    # 15. Role-Specific
    questions.append({
        "type": "Role Specific", "difficulty": "Hard",
        "question": "How do you manage database migrations in a production environment with millions of active rows?",
        "ideal_answer": "Large database migrations are executed online without locking tables. This is done by writing backward-compatible migrations, adding columns as nullable, writing data in batches, and dropping columns only after code updates.",
        "key_points": ["Online migration tools (Alembic)", "Avoiding table locks", "Backward compatibility"],
        "follow_up_questions": ["What is a lock timeout and why set it?", "How do you rollback a failed migration on large tables?"],
        "star_answer": {
            "situation": "We needed to add a non-nullable foreign key to a table with 25 million rows.",
            "task": "I had to deploy the database change with zero table lock time and zero downtime.",
            "action": "I added the column as nullable, populated data in batches, and added the constraint afterward.",
            "result": "The migration completed successfully in production with zero impact on active api queries."
        },
        "short_answer": "I run migrations by adding nullable columns first, backfilling data in chunks, and applying constraints later.",
        "detailed_answer": "To migrate large databases without downtime, follow a multi-step pattern. First, deploy a migration that adds the column as nullable. Second, update code to write to both old and new columns. Third, run a background script to backfill historical rows in chunks. Finally, deploy a constraint migration and clean up the code.",
        "common_mistakes": ["Executing standard ALTER TABLE constraints directly on large active production tables", "Failing to test rollback pathways for complex migration scripts"],
        "confidence_tips": "Detail the nullable-then-constraint strategy. Mention batching and transaction size limits."
    })
    
    return questions

def clean_json_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    if not (cleaned.startswith('{') or cleaned.startswith('[')):
        match = re.search(r'([\[\{].*[\}\]])', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
    return cleaned

def generate_interview_questions(matched_skills, missing_skills, jd_text, api_key=None):
    if not api_key:
        return generate_local_questions(matched_skills, missing_skills)
        
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    ]
    
    prompt = f"""
    You are an expert technical recruiter. Review these matching parameters and Job Description (JD):
    Matched Skills: {', '.join(matched_skills)}
    Missing Skills: {', '.join(missing_skills)}
    JD Summary: {jd_text[:1200]}
    
    Generate exactly 15 distinct screening interview questions of varying difficulties (Easy, Medium, Hard).
    The questions, ideal answers, key points, follow-ups, and STAR answers MUST be highly tailored and specific to the role responsibilities, company context, and requirements described in the Job Description (JD Summary). Avoid generic questions; customize each question to target how the candidate can bridge gaps or apply their matched skills in the specific context of the job.

    The distribution MUST be: 5 Technical, 4 Behavioral, 4 Role Specific, and 2 HR questions.
    Provide for each:
    - type (Technical, Behavioral, Role Specific, HR)
    - difficulty (Easy, Medium, Hard)
    - question
    - ideal_answer
    - key_points (List of strings)
    - follow_up_questions (List of 2 follow ups)
    - star_answer (Object: situation, task, action, result)
    - short_answer
    - detailed_answer
    - common_mistakes (List of strings)
    - confidence_tips
    
    Format the response as a single, valid JSON array of objects. Do not wrap in markdown block text.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=25)
            if response.status_code == 200:
                res_data = response.json()
                content_text = res_data['candidates'][0]['content']['parts'][0]['text']
                cleaned_text = clean_json_text(content_text)
                return json.loads(cleaned_text)
        except Exception as e:
            print(f"Gemini Questions generator exception ({url}): {e}")
            
    return generate_local_questions(matched_skills, missing_skills)

def evaluate_interview_answer_locally(question, user_answer, jd_text=""):
    if not user_answer or not user_answer.strip():
        return {
            "confidence": {"rating": 1, "feedback": "No response provided."},
            "grammar": {"rating": 1, "feedback": "Answer was empty."},
            "technical_accuracy": {"rating": 1, "feedback": "No content to evaluate."},
            "star_structure": {"rating": 1, "feedback": "No structure present."},
            "suggestions": ["• Provide a comprehensive response explaining your approach."],
            "overall_score": 0
        }
        
    answer_clean = user_answer.strip()
    words = answer_clean.split()
    word_count = len(words)
    lower_answer = answer_clean.lower()
    lower_question = question.lower() if question else ""
    lower_jd = jd_text.lower() if jd_text else ""
    
    # 1. TECHNICAL ACCURACY EVALUATION (Dynamic Keyword & Concept Match)
    stop_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'you', 'your', 'describe', 'explain', 'tell', 'me', 'about', 'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'this', 'that', 'these', 'those'}
    
    q_words = set(re.findall(r'\b[a-zA-Z0-9\+\#\.\-]{3,}\b', lower_question)) - stop_words
    jd_words = set(re.findall(r'\b[a-zA-Z0-9\+\#\.\-]{3,}\b', lower_jd)) - stop_words
    
    domain_tech_terms = {
        'api', 'rest', 'python', 'flask', 'docker', 'kubernetes', 'aws', 'sql', 'database', 'git', 
        'architecture', 'query', 'scale', 'scaling', 'index', 'indexing', 'cache', 'redis', 'queue', 
        'celery', 'testing', 'unit', 'cicd', 'pipeline', 'deployment', 'microservices', 'owasp', 
        'security', 'jwt', 'auth', 'oauth', 'concurrency', 'lock', 'locking', 'thread', 'async', 
        'react', 'node', 'express', 'postgresql', 'gunicorn', 'agile', 'scrum', 'star', 'lead', 
        'performance', 'latency', 'throughput', 'metric', 'monitoring', 'postmortem', 'outage'
    }
    
    matched_q_terms = [t for t in q_words if t in lower_answer]
    matched_domain_terms = [t for t in domain_tech_terms if t in lower_answer]
    
    if len(matched_q_terms) >= 2 or len(matched_domain_terms) >= 3:
        accuracy_rating = 5
        accuracy_fb = f"Strong technical relevance. Addresses core concepts ({', '.join((matched_q_terms + matched_domain_terms)[:3])})."
    elif len(matched_q_terms) >= 1 or len(matched_domain_terms) >= 1:
        accuracy_rating = 4
        accuracy_fb = f"Good technical alignment. Touches on key terms like '{matched_q_terms[0] if matched_q_terms else matched_domain_terms[0]}'."
    elif word_count >= 30:
        accuracy_rating = 3
        accuracy_fb = "Relevant general answer, but lacks specific tool references or technical keywords."
    else:
        accuracy_rating = 2
        accuracy_fb = "Limited technical depth. Needs specific methodologies, frameworks, or metrics."

    # 2. STAR STRUCTURE EVALUATION
    situation_keywords = ["situation", "when", "project", "role", "company", "team", "client", "system", "legacy", "surfaced", "faced"]
    task_keywords = ["task", "goal", "objective", "needed to", "had to", "responsibility", "assigned", "required"]
    action_keywords = ["action", "implemented", "built", "designed", "configured", "created", "refactored", "migrated", "resolved", "developed", "used", "applied", "led"]
    result_keywords = ["result", "outcome", "achieved", "improved", "reduced", "decreased", "increased", "percent", "%", "saved", "prevented", "delivered", "successful"]
    
    has_situation = any(k in lower_answer for k in situation_keywords)
    has_task = any(k in lower_answer for k in task_keywords)
    has_action = any(k in lower_answer for k in action_keywords)
    has_result = any(k in lower_answer for k in result_keywords)
    
    star_score = sum([has_situation, has_task, has_action, has_result])
    
    if star_score == 4 or (word_count >= 45 and has_action and has_result):
        structure_rating = 5
        structure_fb = "Excellent STAR flow (Situation, Task, Action, Result clearly articulated)."
    elif star_score == 3 or (word_count >= 35 and has_action):
        structure_rating = 4
        structure_fb = "Solid structure with clear actions and context."
    elif star_score >= 1 or word_count >= 25:
        structure_rating = 3
        structure_fb = "Contains basic narrative flow, but misses quantifiable results or clear task breakdown."
    else:
        structure_rating = 2
        structure_fb = "Lacks structured format. Use the STAR method to organize your points."

    # 3. GRAMMAR & FLUENCY EVALUATION
    filler_words = ["um", "uh", "like", "you know", "basically", "sort of", "kind of", "i mean", "actually"]
    filler_count = sum(lower_answer.count(fw) for fw in filler_words)
    
    sentences = [s for s in re.split(r'[\.\!\?]+', answer_clean) if s.strip()]
    avg_words_per_sentence = word_count / max(1, len(sentences))
    
    if word_count >= 25 and filler_count <= 1 and 6 <= avg_words_per_sentence <= 30:
        grammar_rating = 5
        grammar_fb = "Clear syntax, fluent phrasing, and polished sentence structure."
    elif filler_count <= 2 and word_count >= 15:
        grammar_rating = 4
        grammar_fb = "Good sentence structure and overall readability."
    elif filler_count > 2:
        grammar_rating = 3
        grammar_fb = f"Contains repetitive filler phrases ({filler_count} detected). Practice smoother delivery."
    else:
        grammar_rating = 3
        grammar_fb = "Short answer structure. Form complete sentences to improve delivery."

    # 4. CONFIDENCE EVALUATION
    assertive_verbs = ["architected", "engineered", "championed", "led", "spearheaded", "executed", "optimized", "ensured", "guaranteed", "solved", "delivered", "built", "managed", "drove"]
    hesitant_phrases = ["maybe", "i guess", "i think", "not sure", "sort of", "kind of", "probably", "i try"]
    
    assertive_count = sum(1 for v in assertive_verbs if v in lower_answer)
    hesitant_count = sum(1 for hp in hesitant_phrases if hp in lower_answer)
    
    if assertive_count >= 2 and hesitant_count == 0:
        confidence_rating = 5
        confidence_fb = "Strong, authoritative tone with decisive action verbs."
    elif assertive_count >= 1 or hesitant_count == 0:
        confidence_rating = 4
        confidence_fb = "Confident tone. Clear delivery of your contribution."
    elif hesitant_count >= 1:
        confidence_rating = 3
        confidence_fb = "Slightly hesitant phrasing. Replace qualifiers like 'I think' with definitive action verbs."
    else:
        confidence_rating = 3
        confidence_fb = "Moderate conviction. State your achievements directly."

    # 5. DYNAMIC SUGGESTIONS GENERATION
    suggestions = []
    if word_count < 35:
        suggestions.append("• Elaborate further. Expand your response with concrete examples (aim for 40-75 words).")
    if not has_result:
        suggestions.append("• Include quantifiable outcomes (e.g. 'reduced latency by 30%', 'saved 5 hours weekly').")
    if not matched_q_terms and not matched_domain_terms:
        suggestions.append("• Incorporate specific tools, frameworks, or system concepts relevant to the question.")
    if filler_count > 0:
        suggestions.append(f"• Eliminate filler phrases ({', '.join([f for f in filler_words if f in lower_answer])}) to sound more concise.")
    if hesitant_count > 0:
        suggestions.append("• Replace hesitant phrasing ('I guess', 'maybe') with active leadership statements.")
    if not suggestions:
        suggestions.append("• Outstanding response! Keep up the concise, metric-driven STAR delivery.")

    # 6. OVERALL ACCURACY SCORE CALCULATION
    weighted_score = (
        (accuracy_rating / 5.0) * 35 +
        (structure_rating / 5.0) * 30 +
        (confidence_rating / 5.0) * 20 +
        (grammar_rating / 5.0) * 15
    )
    
    if word_count < 15:
        weighted_score = min(weighted_score, 45)
    elif word_count >= 40:
        weighted_score = min(100, weighted_score + 5)

    overall_score = round(weighted_score)

    return {
        "confidence": {"rating": confidence_rating, "feedback": confidence_fb},
        "grammar": {"rating": grammar_rating, "feedback": grammar_fb},
        "technical_accuracy": {"rating": accuracy_rating, "feedback": accuracy_fb},
        "star_structure": {"rating": structure_rating, "feedback": structure_fb},
        "suggestions": suggestions,
        "overall_score": overall_score
    }

def evaluate_interview_answer(question, user_answer, jd_text, api_key=None):
    if not api_key:
        return evaluate_interview_answer_locally(question, user_answer, jd_text)
        
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    ]
    
    prompt = f"""
    You are an expert AI Interview Coach. Evaluate the candidate's response to the interview question below based on the Job Description.
    
    Job Description:
    {jd_text[:1200]}
    
    Question:
    "{question}"
    
    Candidate's Response:
    "{user_answer}"
    
    Evaluate based on the following fields:
    - confidence: (Object: rating (integer 1-5), feedback (string))
    - grammar: (Object: rating (integer 1-5), feedback (string))
    - technical_accuracy: (Object: rating (integer 1-5), feedback (string))
    - star_structure: (Object: rating (integer 1-5), feedback (string))
    - suggestions: (Array of strings outlining specific improvements, starting with '• ')
    - overall_score: (Integer 0-100 summarizing candidate performance)
    
    Format the response as a single, valid JSON object. Do not wrap in markdown block text.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            if response.status_code == 200:
                res_data = response.json()
                content_text = res_data['candidates'][0]['content']['parts'][0]['text']
                cleaned_text = clean_json_text(content_text)
                return json.loads(cleaned_text)
        except Exception as e:
            print(f"Gemini mock answer evaluation exception ({url}): {e}")
            
    return evaluate_interview_answer_locally(question, user_answer, jd_text)

