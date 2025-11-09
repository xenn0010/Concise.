"""
RIGOROUS TESTING: Does Concise actually deliver on its promises?
Testing with REAL AI agent use cases to verify claims
"""
import requests
import json
import time

API_KEY = "csk_live_x3xPv7y5L3FbUBM_1gebMM8vlibydeXSsmvYPez56ak"
BASE_URL = "http://localhost:8000"

def test_compression(text, name, description):
    """Test compression and return detailed analysis"""
    print(f"\n{'='*90}")
    print(f"TEST: {name}")
    print(f"Description: {description}")
    print(f"{'='*90}")
    print(f"Input length: {len(text)} characters")
    print(f"First 150 chars: {text[:150]}...")

    try:
        response = requests.post(
            f"{BASE_URL}/v1/compress",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            },
            json={
                "text": text,
                "level": "aggressive"
            },
            timeout=180
        )

        if response.status_code == 200:
            result = response.json()
            reduction_pct = (1 - result['compression_ratio']) * 100

            print(f"\n✅ COMPRESSION SUCCESSFUL")
            print(f"   Original tokens:      {result['original_tokens']:,}")
            print(f"   Compressed tokens:    {result['compressed_tokens']:,}")
            print(f"   Tokens saved:         {result['tokens_saved']:,}")
            print(f"   Reduction:            {reduction_pct:.1f}%")
            print(f"   Strategy used:        {result['strategy']}")
            print(f"   Processing time:      {result['compression_time_ms']:.2f}ms")

            # Cost analysis
            gpt4_input_cost = 0.01  # $0.01 per 1K tokens
            claude_opus_cost = 0.015  # $0.015 per 1K tokens

            gpt4_savings = (result['tokens_saved'] / 1000) * gpt4_input_cost
            claude_savings = (result['tokens_saved'] / 1000) * claude_opus_cost

            print(f"\n💰 COST SAVINGS PER REQUEST:")
            print(f"   GPT-4:                ${gpt4_savings:.6f}")
            print(f"   Claude Opus:          ${claude_savings:.6f}")

            print(f"\n📊 AT SCALE (100K requests/month):")
            print(f"   GPT-4 savings:        ${gpt4_savings * 100000:,.2f}/month")
            print(f"   Claude Opus savings:  ${claude_savings * 100000:,.2f}/month")

            print(f"\n📄 COMPRESSED OUTPUT PREVIEW:")
            print(f"   {result['compressed_text'][:200]}...")

            return {
                'success': True,
                'original_tokens': result['original_tokens'],
                'compressed_tokens': result['compressed_tokens'],
                'tokens_saved': result['tokens_saved'],
                'reduction_pct': reduction_pct,
                'strategy': result['strategy'],
                'gpt4_savings_per_100k': gpt4_savings * 100000
            }
        else:
            print(f"\n❌ COMPRESSION FAILED")
            print(f"   Status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return {'success': False, 'error': response.text}

    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED")
        print(f"   Error: {str(e)}")
        return {'success': False, 'error': str(e)}


print("="*90)
print("CONCISE COMPRESSION - RIGOROUS REAL-WORLD TESTING")
print("Testing claims: Does it actually work? What are the real savings?")
print("="*90)

results = []

# ==============================================================================
# TEST 1: Python Code (Our claimed 39% reduction)
# ==============================================================================
python_code = """
def process_user_authentication(username, password, remember_me=False):
    '''
    Authenticate a user with the given credentials.

    This function handles user authentication by validating credentials
    against the database, checking password hashes, and creating session
    tokens for authenticated users.

    Args:
        username (str): The username to authenticate
        password (str): The plain text password to verify
        remember_me (bool): Whether to create a long-lived session

    Returns:
        dict: Authentication result with user info and token

    Raises:
        AuthenticationError: If credentials are invalid
        DatabaseError: If database connection fails
    '''
    # First, validate input parameters
    if not username or not password:
        raise ValueError("Username and password are required")

    # Fetch user from database
    user = database.get_user_by_username(username)

    # Check if user exists
    if not user:
        # Log failed attempt for security monitoring
        logger.warning(f"Failed login attempt for username: {username}")
        raise AuthenticationError("Invalid credentials")

    # Verify password hash
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        # Log failed attempt
        logger.warning(f"Invalid password for user: {username}")
        raise AuthenticationError("Invalid credentials")

    # Check if account is active
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    # Generate session token
    session_duration = 30 if remember_me else 1  # days
    token = generate_jwt_token(user.id, duration_days=session_duration)

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    database.save(user)

    # Return authentication result
    return {
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name
        },
        'token': token,
        'expires_at': (datetime.utcnow() + timedelta(days=session_duration)).isoformat()
    }


class UserManager:
    '''
    Manages user-related operations including creation, updates, and deletion.

    This class provides a high-level interface for user management operations,
    handling validation, database interactions, and business logic related to users.
    '''

    def __init__(self, database_connection):
        '''Initialize the UserManager with a database connection.'''
        self.db = database_connection
        self.logger = logging.getLogger(__name__)

    def create_user(self, username, email, password, full_name=None):
        '''
        Create a new user account.

        Args:
            username (str): Unique username for the account
            email (str): User's email address
            password (str): Plain text password (will be hashed)
            full_name (str, optional): User's full name

        Returns:
            User: The newly created user object
        '''
        # Validate email format
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")

        # Check if username already exists
        if self.db.get_user_by_username(username):
            raise ValueError("Username already exists")

        # Hash password before storing
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create user object
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            is_active=True,
            created_at=datetime.utcnow()
        )

        # Save to database
        self.db.save(user)
        self.logger.info(f"Created new user: {username}")

        return user
"""

results.append(test_compression(
    python_code,
    "Python Code Compression",
    "Testing our claimed 39% reduction on Python code with comments and docstrings"
))

# ==============================================================================
# TEST 2: JavaScript/TypeScript Code (Currently unsupported)
# ==============================================================================
javascript_code = """
/**
 * Process payment transaction with fraud detection
 *
 * This function handles credit card payments, performs fraud checks,
 * and creates transaction records in the database.
 *
 * @param {Object} paymentData - Payment information
 * @param {string} paymentData.cardNumber - Credit card number
 * @param {string} paymentData.cvv - Card verification value
 * @param {number} paymentData.amount - Payment amount in cents
 * @param {string} paymentData.currency - Three-letter currency code
 * @returns {Promise<Object>} Transaction result with status and details
 * @throws {PaymentError} If payment processing fails
 */
async function processPayment(paymentData) {
    // Validate required fields
    if (!paymentData || !paymentData.cardNumber || !paymentData.amount) {
        throw new PaymentError('Missing required payment information');
    }

    // Check for fraud indicators
    const fraudScore = await checkFraudScore(paymentData);

    if (fraudScore > 0.8) {
        // High fraud risk - reject transaction
        logger.warn(`High fraud score detected: ${fraudScore}`);
        throw new PaymentError('Transaction declined - fraud detected');
    }

    // Process payment through payment gateway
    try {
        const result = await paymentGateway.charge({
            amount: paymentData.amount,
            currency: paymentData.currency || 'USD',
            source: paymentData.cardNumber,
            description: paymentData.description
        });

        // Save transaction record
        const transaction = await database.transactions.create({
            amount: paymentData.amount,
            currency: paymentData.currency,
            status: 'completed',
            gateway_transaction_id: result.id,
            fraud_score: fraudScore,
            created_at: new Date()
        });

        // Return success response
        return {
            success: true,
            transaction_id: transaction.id,
            amount: paymentData.amount,
            status: 'completed'
        };

    } catch (error) {
        // Log error for debugging
        logger.error('Payment processing failed:', error);

        // Create failed transaction record
        await database.transactions.create({
            amount: paymentData.amount,
            status: 'failed',
            error_message: error.message,
            created_at: new Date()
        });

        throw new PaymentError('Payment processing failed');
    }
}

/**
 * User authentication service
 */
class AuthenticationService {
    constructor(config) {
        this.config = config;
        this.tokenExpiry = config.tokenExpiry || 3600; // 1 hour default
    }

    /**
     * Authenticate user with email and password
     *
     * @param {string} email - User email address
     * @param {string} password - User password
     * @returns {Promise<Object>} Authentication token and user data
     */
    async authenticate(email, password) {
        // Find user by email
        const user = await database.users.findOne({ email: email });

        if (!user) {
            throw new AuthError('Invalid credentials');
        }

        // Verify password
        const isValid = await bcrypt.compare(password, user.password_hash);

        if (!isValid) {
            throw new AuthError('Invalid credentials');
        }

        // Generate JWT token
        const token = jwt.sign(
            { userId: user.id, email: user.email },
            this.config.jwtSecret,
            { expiresIn: this.tokenExpiry }
        );

        return {
            token: token,
            user: {
                id: user.id,
                email: user.email,
                name: user.name
            }
        };
    }
}
"""

results.append(test_compression(
    javascript_code,
    "JavaScript Code Compression",
    "Testing JS/TS code - currently falls back to text compression (expected to perform poorly)"
))

# ==============================================================================
# TEST 3: Large System Prompt (AI Agent Use Case)
# ==============================================================================
system_prompt = """You are an expert software engineering assistant with comprehensive knowledge of modern development practices, programming languages, frameworks, and system architecture. Your primary role is to help developers solve complex technical challenges, debug issues, design scalable systems, and write production-quality code.

When providing assistance, you must strictly follow these guidelines and best practices:

1. Code Quality and Correctness:
   - Always prioritize code correctness, maintainability, and readability above clever optimizations
   - Write code that follows the language's idioms and community best practices
   - Include proper error handling for all edge cases and failure scenarios
   - Add meaningful comments that explain WHY, not just WHAT the code does
   - Use descriptive variable and function names that make the code self-documenting

2. Security Awareness:
   - Be vigilant about common security vulnerabilities including SQL injection, XSS, CSRF, authentication bypasses, and insecure data handling
   - Never store sensitive data like passwords, API keys, or tokens in plain text
   - Always validate and sanitize user input before processing
   - Use parameterized queries for database operations to prevent SQL injection
   - Implement proper authentication and authorization checks
   - Follow the principle of least privilege in all security-related decisions

3. Technical Explanations:
   - Provide clear, detailed explanations that help developers understand the underlying concepts
   - Include relevant code examples that demonstrate the solution in action
   - Explain trade-offs between different approaches when multiple solutions exist
   - Consider factors like performance, scalability, maintainability, and complexity
   - If you're uncertain about something, clearly state your uncertainty rather than guessing

4. Performance and Scalability:
   - Consider performance implications of your recommendations
   - Suggest appropriate data structures and algorithms for the problem complexity
   - Be aware of common performance pitfalls in different languages and frameworks
   - Think about how the solution will scale with increased load or data volume
   - Recommend caching strategies, database indexing, and query optimization when relevant

5. Testing and Quality Assurance:
   - Advocate for comprehensive testing at unit, integration, and end-to-end levels
   - Suggest appropriate test cases including edge cases and error conditions
   - Recommend test-driven development approaches when beneficial
   - Consider testability when designing code architecture

Your areas of expertise include but are not limited to:

Backend Development:
- Python ecosystem (Django, Flask, FastAPI, asyncio, Celery)
- Node.js and TypeScript (Express, NestJS, Fastify)
- Java and Spring Boot framework
- Go for high-performance services
- Rust for systems programming

Frontend Development:
- Modern JavaScript (ES6+, async/await, modules)
- React with hooks and context
- Vue.js 3 with composition API
- TypeScript for type-safe frontend code
- State management (Redux, Vuex, Pinia)
- CSS frameworks and methodologies

Databases and Data Storage:
- SQL databases (PostgreSQL, MySQL) with complex queries and optimization
- NoSQL databases (MongoDB, Redis, Cassandra)
- Database design, normalization, and indexing strategies
- ORMs and query builders
- Caching strategies and implementation

Cloud and DevOps:
- Containerization with Docker and orchestration with Kubernetes
- AWS, Azure, and Google Cloud Platform services
- CI/CD pipelines and automation
- Infrastructure as Code (Terraform, CloudFormation)
- Monitoring, logging, and observability

System Architecture:
- Microservices architecture and design patterns
- RESTful API design and GraphQL
- Event-driven architectures and message queues
- Distributed systems and consistency patterns
- Load balancing and horizontal scaling

Always provide responses that are professional, technically accurate, and genuinely helpful to developers at all skill levels."""

results.append(test_compression(
    system_prompt,
    "Large System Prompt (AI Agent)",
    "Real-world AI agent system prompt - 500+ tokens of instructions"
))

# ==============================================================================
# TEST 4: RAG Documentation Context
# ==============================================================================
rag_documentation = """# Complete Guide to PostgreSQL Database Optimization

## Introduction to PostgreSQL Performance

PostgreSQL is a powerful, open-source relational database management system that offers excellent performance characteristics when properly configured and optimized. However, achieving optimal performance requires understanding various aspects of database design, query optimization, indexing strategies, and server configuration. This comprehensive guide covers the essential techniques and best practices for maximizing PostgreSQL performance in production environments.

## Understanding Query Execution Plans

The foundation of query optimization is understanding how PostgreSQL executes queries. The query planner analyzes your SQL statements and generates an execution plan that determines the most efficient way to retrieve the requested data. You can view the execution plan using the EXPLAIN command, which shows the steps PostgreSQL will take to execute your query.

The EXPLAIN ANALYZE command goes one step further by actually executing the query and showing the actual execution time for each step. This is invaluable for identifying performance bottlenecks in your queries. When analyzing execution plans, pay attention to sequential scans on large tables, nested loop joins that process many rows, and operations that require sorting large result sets.

## Indexing Strategies for Optimal Performance

Indexes are the most powerful tool for improving query performance in PostgreSQL. A well-designed index can reduce query execution time from seconds or minutes to milliseconds. However, indexes come with trade-offs: they consume disk space and slow down write operations (INSERT, UPDATE, DELETE) because the indexes must be updated whenever data changes.

B-tree indexes are the default and most commonly used index type. They work well for equality and range queries on columns with many distinct values. Use B-tree indexes for primary keys, foreign keys, and columns frequently used in WHERE clauses with operators like =, <, >, <=, >=, and BETWEEN.

Hash indexes are optimized for equality comparisons only. They can be slightly faster than B-tree indexes for equality lookups but don't support range queries. In most cases, B-tree indexes are preferred because of their versatility.

GIN (Generalized Inverted Index) indexes are ideal for indexing array columns, JSONB data, and full-text search. They're particularly effective when a single column value can contain multiple component values, such as arrays or documents with many words.

BRIN (Block Range Index) indexes are extremely space-efficient for very large tables where the column values have natural clustering. They're perfect for timestamp columns in time-series data where rows are inserted in chronological order.

## Query Optimization Techniques

Writing efficient SQL queries is essential for database performance. Start by selecting only the columns you need rather than using SELECT *. This reduces the amount of data transferred and processed. Use appropriate JOIN types based on your data relationships and query requirements.

When filtering data, put the most selective conditions first in your WHERE clause. This helps PostgreSQL eliminate rows as early as possible in the query execution. Use EXISTS instead of IN for subqueries when checking for existence, as EXISTS can short-circuit once a match is found.

Avoid using functions on indexed columns in WHERE clauses, as this prevents index usage. Instead of WHERE UPPER(name) = 'JOHN', create a functional index or restructure the query. Use parameterized queries to allow PostgreSQL to cache and reuse query plans.

## Connection Pooling and Resource Management

Database connections are expensive resources that consume memory and processing power. Connection pooling maintains a pool of reusable database connections that can be shared across application requests. This dramatically reduces the overhead of establishing new connections for each database operation.

Popular connection pooling solutions for PostgreSQL include PgBouncer, which operates as a lightweight external process, and built-in pooling in application frameworks. Configure your pool size based on your application's concurrency requirements and database server resources. A good starting point is to set the pool size equal to the number of CPU cores on your database server.

## Vacuuming and Maintenance

PostgreSQL uses Multi-Version Concurrency Control (MVCC) to handle concurrent transactions. This creates dead tuples that must be cleaned up through the VACUUM process. Dead tuples consume disk space and slow down queries by forcing the database to scan unnecessary data.

The autovacuum daemon automatically runs VACUUM and ANALYZE operations on your tables. However, for tables with high update or delete rates, you may need to tune autovacuum settings or run manual VACUUM operations during maintenance windows. Regular VACUUM operations prevent table bloat and maintain query performance.

The ANALYZE operation collects statistics about the distribution of data in your tables. These statistics are crucial for the query planner to generate efficient execution plans. Run ANALYZE after bulk data loads or significant data changes to ensure the planner has accurate information.

## Monitoring and Diagnostic Tools

Effective performance tuning requires continuous monitoring and analysis. PostgreSQL provides numerous system views and functions for monitoring database activity. The pg_stat_activity view shows currently running queries and their execution time. Use this to identify long-running queries that may need optimization.

The pg_stat_statements extension tracks execution statistics for all SQL statements executed on your server. It shows total execution time, number of calls, and rows processed for each query. This is invaluable for identifying the queries that consume the most database resources.

For detailed performance analysis, enable query logging with appropriate thresholds. Configure log_min_duration_statement to log queries exceeding a specified duration. Review these logs regularly to identify optimization opportunities.

## Configuration Tuning

PostgreSQL's default configuration is conservative and suitable for systems with limited resources. Production deployments benefit significantly from tuning configuration parameters based on available hardware and workload characteristics.

The shared_buffers parameter controls how much memory PostgreSQL uses for caching data. A good starting point is 25% of available RAM, up to about 8-16 GB on systems with large amounts of memory. The effective_cache_size parameter hints to the planner about the total memory available for caching, including both PostgreSQL buffers and operating system cache.

For write-heavy workloads, increase wal_buffers and checkpoint_segments to reduce I/O overhead. The work_mem parameter controls memory available for sort and hash operations in individual queries. Set this carefully as each connection can allocate this amount of memory multiple times.

## Partitioning for Large Tables

Table partitioning divides large tables into smaller, more manageable pieces while maintaining the appearance of a single table to applications. This improves query performance by allowing PostgreSQL to scan only relevant partitions instead of the entire table. Partitioning also facilitates data archival and deletion operations.

Range partitioning divides data based on column value ranges, such as dates or numeric ranges. This is ideal for time-series data where queries typically filter by date. List partitioning divides data based on specific column values, useful when data naturally divides into distinct categories. Hash partitioning distributes data evenly across partitions based on a hash function, useful for load balancing.

When implementing partitioning, ensure queries include the partition key in WHERE clauses to enable partition pruning. Create indexes on individual partitions rather than the parent table for better performance."""

results.append(test_compression(
    rag_documentation,
    "RAG Documentation Context",
    "Large technical documentation typical in RAG systems - 1000+ tokens"
))

# ==============================================================================
# TEST 5: Short Text (Expected to fail)
# ==============================================================================
short_text = "The quick brown fox jumps over the lazy dog. This is a test."

results.append(test_compression(
    short_text,
    "Short Text (Control Test)",
    "Short simple text - expected to show minimal/no compression"
))

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "="*90)
print("FINAL ANALYSIS: DOES CONCISE ACTUALLY WORK?")
print("="*90)

successful_tests = [r for r in results if r.get('success')]
failed_tests = [r for r in results if not r.get('success')]

print(f"\nTests completed: {len(results)}")
print(f"Successful: {len(successful_tests)}")
print(f"Failed: {len(failed_tests)}")

if successful_tests:
    total_original = sum(r['original_tokens'] for r in successful_tests)
    total_compressed = sum(r['compressed_tokens'] for r in successful_tests)
    total_saved = sum(r['tokens_saved'] for r in successful_tests)
    avg_reduction = sum(r['reduction_pct'] for r in successful_tests) / len(successful_tests)

    print(f"\n📊 AGGREGATE RESULTS:")
    print(f"   Total original tokens:    {total_original:,}")
    print(f"   Total compressed tokens:  {total_compressed:,}")
    print(f"   Total tokens saved:       {total_saved:,}")
    print(f"   Average reduction:        {avg_reduction:.1f}%")

    total_gpt4_savings = sum(r.get('gpt4_savings_per_100k', 0) for r in successful_tests)
    print(f"\n💰 TOTAL COST SAVINGS (100K requests/month):")
    print(f"   GPT-4: ${total_gpt4_savings:,.2f}/month = ${total_gpt4_savings * 12:,.2f}/year")

print("\n" + "="*90)
print("VERDICT: Can Concise compete at VibeCon?")
print("="*90)
