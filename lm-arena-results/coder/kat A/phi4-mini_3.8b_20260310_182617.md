# Model: phi4-mini:3.8b
**Test Date:** 2026-03-10 18:55:17
**Total Questions:** 12

---

## Question 1
**Q:** You are designing a REST API for a multi-tenant SaaS project management tool.
Entities: Workspace, Project, Task, User, Comment.

Rules:
- A user can belong to multiple workspaces
- Projects belong to a workspace
- Tasks belong to a project and can be assigned to users
- Comments belong to tasks

Design the complete API:
1. Define all endpoints (method + path) following REST conventions
2. Show request/response JSON shapes for: create task, update task status, list tasks with filters (assignee, status, due date), add comment
3. Define your error response format — be consistent across all endpoints
4. How do you handle pagination? Show the response envelope
5. Which endpoints need which HTTP status codes and when?

Do NOT write server code — this is a design question. Clarity and consistency matter most.

**A:**
Endpoint Definitions:

1. Workspace endpoints:
- List Workspaces: GET /api/workspaces
- Create Workspace: POST /api/workspaces
- Update Workspace: PUT /api/workspaces/{workspaceId}
- Delete Workspace: DELETE /api/workspaces/{workspaceId}

2. Project endpoints:
- List Projects: GET /api/workspaces/{workspaceId}/projects
- Create Project: POST /api/workspaces/{workspaceId}/projects
- Update Project: PUT /api/workspaces/{workspaceId}/projects/{projectId}
- Delete Project: DELETE /api/workspaces/{workspaceId}/projects/{projectId}

3. Task endpoints:
- List Tasks: GET /api/workspaces/{workspaceId}/projects/{projectId}/tasks
- Create Task: POST /api/workspaces/{workspaceId}/projects/{projectId}/tasks
- Update Task: PUT /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
- Update Task Status: PATCH /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
- Delete Task: DELETE /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}

4. User endpoints:
- List Users: GET /api/workspaces/{workspaceId}/users
- Create User: POST /api/workspaces/{workspaceId}/users
- Update User: PUT /api/workspaces/{workspaceId}/users/{userId}
- Delete User: DELETE /api/workspaces/{workspaceId}/users/{userId}

5. Comment endpoints:
- List Comments: GET /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments
- Create Comment: POST /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments
- Delete Comment: DELETE /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}

Request/Response JSON Shapes:

1. Create Task:
Request:
```json
{
  "name": "Task Name",
  "description": "Task Description",
  "assignee": "User Id",
  "due_date": "Due Date"
}
```
Response:
```json
{
  "taskId": "taskId",
  "name": "Task Name",
  "description": "Task Description",
  "assignee": "User Id",
  "due_date": "Due Date",
  "status": "Created"
}
```

2. Update Task Status:
Request:
```json
{
  "status": "In Progress"
}
```
Response:
```json
{
  "taskId": "task

*Response time: 8.1s*

---

## Question 2
**Q:** Implement the following endpoint in Node.js + Express + TypeScript:

PATCH /workspaces/:workspaceId/tasks/:taskId

Requirements:
- Partial update: only fields provided in the body should change
- Allowed fields: title (string, 1-200 chars), status (todo|in_progress|done|cancelled), assignee_id (integer or null), due_date (ISO8601 or null)
- Validate that workspaceId and taskId are valid integers
- Validate that the task belongs to the workspace (return 404 if not)
- Validate that assignee_id (if provided) is a member of the workspace
- Return 400 with field-level validation errors if validation fails
- Return 409 if trying to set status to 'cancelled' when task has open subtasks
- Use Zod for validation
- Write the complete handler + validation schema + error middleware
- Write 4 unit tests covering: success, validation error, 404, 409

**A:**
To implement the specified endpoint and requirements using Node.js + Express + TypeScript, follow these steps:

1. **Install dependencies:**
```bash
npm install express zod
npm install @types/express @types/node typescript ts-node @types/node
```

2. **Create the TypeScript configuration file (tsconfig.json):**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

3. **Create the main server file (server.ts):**
```typescript
import express, { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { zodResolver } from 'zod';
import { randomUUID } from 'crypto';

interface Workspace {
  id: number;
  name: string;
  members: string[]; // Array of assignee_ids
}

interface Task {
  id: number;
  title: string;
  status: 'todo' | 'in_progress' | 'done' | 'cancelled';
  assignee_id: number | null;
  due_date: string | null;
}

interface Workspaces {
  [id: number]: Workspace;
}

const app = express();
app.use(express.json());

const workspaces: Workspaces = {
  1: { id: 1, name: 'Workspace 1', members: ['1', '2'] },
  2: { id: 2, name: 'Workspace 2', members: ['3'] },
};

app.put('/workspaces/:workspaceId/tasks/:taskId', async (req: Request, res: Response) => {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;

  const workspace = workspaces[parseInt(workspaceId, 10)];
  if (!workspace) {
    return res.status(404).send({ message: 'Workspace not found' });
  }

  const task = workspaces[workspaceId].tasks.find(t => t.id === parseInt(taskId, 10));
  if (!task) {
    return res.status(404).send({ message: 'Task not found' });
  }

  const validationResult = validateUpdate({
    title,
    status,
    assignee_id,
    due_date,
  });

  if (!validationResult.success) {
    return res.status(400).json(validationResult.error);
  }

  if (status === 'cancelled' && task.status !== 'done') {
    return res.status(409).send({ message: 'Cannot cancel task with open subtasks' });
  }

  const updatedTask = { ...task, ...validationResult.data };
  workspaces[workspaceId].tasks[taskId] = updatedTask;

  res.send(updatedTask);
});

const validationSchema = z.object({
  title: z.string().min(1, { message: 'Title is required' }).max(200, { message: 'Title is too long' }),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: z.string().optional(),
  due_date: z.string().optional(),
}).refine(data => {
  if (data.status === 'cancelled' && !data.subtasks.every(t => t.status === 'done')) {
    throw new Error('Cannot cancel task with open subtasks');
  }
}, { message: 'Validation failed' });

const validateUpdate = (data: { title?: string; status?: string; assignee_id?: number | null; due_date?: string | null } = {}) =>
  validationSchema.safeParse({ ...data });

app.use((err, req, res, next) => {
  res.status(500).json({ message: err.message });
});

app.listen(3000, () => console.log('Server is running on http://localhost:3000'));
```

4. **Write the 4 unit tests (unit-tests.ts):**
```typescript
import request from 'supertest';
import app from './server';

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  it('should update task successfully', async () => {
    const res = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({
        title: 'Updated Title',
        status: 'in_progress',
      });
    expect(res.status).toEqual(200);
    expect(res.body).toEqual({ title: 'Updated Title', status: 'in_progress' });
  });

  it('should return 400 with field-level validation errors', async () => {
    const res = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({
        title: 'Too long title...',
      });
    expect(res.status).toEqual(400);
    expect(res.body).toEqual({
      success: false,
      error: {
        title: 'Title is too long',
      },
    });
  });

  it('should return 404 if workspace not found', async () => {
    const res = await request(app)
      .patch('/workspaces/999/tasks/1')
      .send({
        title: 'Updated Title',
        status: 'in_progress',
      });
    expect(res.status).toEqual(404);
  });

  it('should return 409 if trying to cancel task with open subtasks', async () => {
    const res = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({
        title: 'Updated Title',
        status: 'cancelled',
      });
    expect(res.status).toEqual(409);
  });
});

```

5. **Run the tests:**
```bash
npm install supertest jest ts-jest @types/jest @types/supertest --save-dev
npx ts-jest config:init
npx jest unit-tests.ts
```

6. **Run the server:**
```bash
ts-node server.ts
```

**Note:**
- This code provides a basic implementation of the endpoint and its requirements.
- The `workspaces` and `tasks` data structures should ideally be stored in a database, and you would need to implement appropriate data access logic for a complete and robust solution.
- Make sure to replace the inline data storage with actual database queries.
- Adjust the code to fit your project structure and coding standards.

*Response time: 18.8s*

---

## Question 3
**Q:** Implement a complete authentication system in Node.js + Express + TypeScript:

1. POST /auth/register — email + password, hash password with bcrypt (cost factor 12), return user object (no password)
2. POST /auth/login — validate credentials, return access token (15min expiry) + refresh token (7 days), store refresh token in httpOnly cookie
3. GET /auth/me — protected route, return current user from token
4. JWT payload should contain: userId, email, role, iat, exp
5. Write authMiddleware that validates the access token and attaches user to req.user
6. What happens if someone sends an expired token? Show the exact error response.
7. Why httpOnly cookie for refresh token instead of localStorage? Explain the security reasoning.

**A:**
Sure! Here's a complete authentication system using Node.js, Express, and TypeScript. Note that you'll need to install several npm packages (`express`, `jsonwebtoken`, `bcrypt`, `cookie-parser`, `cors`, etc.) for this to work.

### 1. Setup your Node.js + Express + TypeScript environment:

First, create a new directory for your project and initialize it:

```bash
mkdir auth-system
cd auth-system
npm init -y
npm install express jsonwebtoken bcrypt cookie-parser cors dotenv
npm install -D typescript @types/node @types/express @types/jsonwebtoken @types/bcrypt @types/cookie-parser @types/cors
```

Then, create a `tsconfig.json` for TypeScript configuration:

```json
{
  "compilerOptions": {
    "target": "ES6",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "./dist"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### 2. Create the main application files:

- `src/index.ts`
- `src/middleware/authMiddleware.ts`
- `src/models/User.ts`
- `src/routes/authRoutes.ts`
- `src/utils/tokenUtil.ts`
- `src/utils/helper.ts`

### 3. Implement the routes and middleware:

#### `src/models/User.ts`

```typescript
import * as bcrypt from 'bcrypt';
import * as mongoose from 'mongoose';

interface IUser extends mongoose.Document {
  _id: mongoose.Types.ObjectId;
  email: string;
  password: string;
  role: string;
  iat: number;
  exp: number;
}

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, default: 'user' }
});

userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

const User = mongoose.model<IUser>('User', userSchema);

export default User;
```

#### `src/middleware/authMiddleware.ts`

```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import User from '../models/User';

export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers['authorization']?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Unauthorized' });

    const decoded = jwt.verify(token, process.env.JWT_SECRET) as any;
    const user = await User.findOne({ _id: decoded.userId });
    if (!user) return res.status(401).json({ error: 'Unauthorized' });

    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Unauthorized: Token expired' });
    }
    return res.status(401).json({ error: 'Unauthorized' });
  }
};
```

#### `src/utils/tokenUtil.ts`

```typescript
import jwt from 'jsonwebtoken';

const generateTokens = (userId: string, email: string, role: string) => {
  const payload = {
    userId,
    email,
    role,
    iat: Math.floor(Date.now() / 1000),
  };
  const accessToken = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '15m' });
  const refreshToken = jwt.sign(payload, process.env.JWT_REFRESH_SECRET, { expiresIn: '7d' });

  return { accessToken, refreshToken };
};
```

#### `src/routes/authRoutes.ts`

```typescript
import express, { Request, Response } from 'express';
import User from '../models/User';
import { generateTokens, authMiddleware } from '../utils/tokenUtil';

const router = express.Router();

// Register endpoint
router.post('/auth/register', async (req: Request, res: Response) => {
  const { email, password } = req.body;
  try {
    const existingUser = await User.findOne({ email });
    if (existingUser) return res.status(400).json({ error: 'Email already in use' });

    const user = new User({ email, password });
    await user.save();

    const tokens = generateTokens(user._id.toString(), user.email, 'user');
    res.status(201).json({ ...tokens });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Login endpoint
router.post('/auth/login', async (req: Request, res: Response) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(401).json({ error: 'Unauthorized' });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(401).json({ error: 'Invalid credentials' });

    const tokens = generateTokens(user._id.toString(), user.email, user.role);
    res.cookie('refreshToken', tokens.refreshToken, {
      httpOnly: true,
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.status(200).json({ ...tokens });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get current user
router.get('/auth/me', authMiddleware, (req: Request, res: Response) => {
  res.status(200).json(req.user);
});

export default router;
```

#### `src/utils/helper.ts`

```typescript
export const setCookies = (res: any, name: string, value: string, options?: { httpOnly?: boolean }) => {
  res.cookie(name, value, options);
};
```

#### `src/index.ts`

```typescript
import express from 'express';
import bodyParser from 'body-parser';
import mongoose from 'mongoose';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import { authRoutes } from './routes/authRoutes';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(bodyParser.json());
app.use(cookieParser());
app.use(cors({ credentials: true, origin: 'http://localhost:3000' }));

mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true });

app.use('/auth', authRoutes);

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on http://localhost:${port}`));
```

### 4. Environment variables (`.env`):

```
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
JWT_REFRESH_SECRET=your_jwt_refresh_secret
```

### 5. Run your server:

```bash
npx ts-node src/index.ts
```

### 6. Security Reasoning for httpOnly Cookie for Refresh Token:

Using `httpOnly` cookies for the refresh token instead of local storage or other client-side storage mechanisms significantly improves security by mitigating the risk of cross-site scripting (XSS) attacks. If an attacker can inject malicious scripts into your application, they can potentially access the refresh token stored in local storage. By using `httpOnly` cookies, the token is not accessible via JavaScript, thereby protecting it from being stolen by XSS attacks.

Additionally, using httpOnly cookies helps prevent access to the refresh token by malicious third-party scripts running in the browser, as they cannot read or manipulate cookies set with the `httpOnly` flag. This further enhances the security of your authentication system by limiting the potential attack surface.

*Response time: 23.3s*

---

## Question 4
**Q:** Continuing from the previous auth system:

1. POST /auth/refresh — use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).
2. POST /auth/logout — invalidate the refresh token, clear the cookie
3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy)
4. How do you handle the case where a refresh token is used twice? (token reuse detection) — implement it
5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.
6. What is the difference between token blacklisting and token rotation? When would you use each?

**A:**
To continue from the previous authentication system, we can implement the requested functionalities step-by-step. Here's how we can approach each of the tasks:

1. **POST /auth/refresh**: 
   - Use the refresh token from the cookie to issue a new access token.
   - Rotate the refresh token by issuing a new one and invalidating the old one.

   ```python
   from flask import Flask, request, jsonify, make_response
   import jwt
   from datetime import datetime, timedelta
   import redis
   import uuid

   app = Flask(__name__)
   redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

   SECRET_KEY = 'your_secret_key'

   def generate_access_token(user_id):
       payload = {
           'user_id': user_id,
           'exp': datetime.utcnow() + timedelta(minutes=15)  # 15 minutes expiry
       }
       return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

   def generate_refresh_token(user_id):
       payload = {
           'user_id': user_id,
           'type': 'refresh',
           'exp': datetime.utcnow() + timedelta(days=7)  # 1 week expiry
       }
       return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

   @app.route('/auth/refresh', methods=['POST'])
   def refresh_token():
       refresh_token = request.cookies.get('refresh_token')
       try:
           decoded_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
           if decoded_token['type'] == 'refresh':
               user_id = decoded_token['user_id']
               new_refresh_token = generate_refresh_token(user_id)
               response = make_response(jsonify({'access_token': generate_access_token(user_id)}))
               response.set_cookie('refresh_token', new_refresh_token, httponly=True)
               redis_client.set(f'refresh_token:{user_id}', new_refresh_token, ex=86400)  # TTL 1 day
               return response
           else:
               return jsonify({'error': 'Invalid refresh token'}), 401
       except Exception as e:
           return jsonify({'error': str(e)}), 500

   @app.route('/auth/logout', methods=['POST'])
   def logout():
       refresh_token = request.cookies.get('refresh_token')
       decoded_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
       user_id = decoded_token['user_id']
       redis_client.delete(f'refresh_token:{user_id}')
       response = make_response(jsonify({'message': 'Logged out successfully'}))
       response.set_cookie('refresh_token', '', httponly=True, expires=0)
       return response

   def validate_token(token):
       try:
           decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
           if decoded_token['type'] == 'refresh':
               return decoded_token
           return None
       except Exception as e:
           return None

   def refresh_token_used_twice():
       refresh_token = request.cookies.get('refresh_token')
       decoded_token = validate_token(refresh_token)
       if decoded_token:
           user_id = decoded_token['user_id']
           current_refresh_token = redis_client.get(f'refresh_token:{user_id}')
           if current_refresh_token != decoded_token:
               return jsonify({'error': 'Token reused twice'}), 400
           redis_client.delete(f'refresh_token:{user_id}')
       return None

   app.before_request(lambda: refresh_token_used_twice() if 'refresh_token' in request.cookies else None)

   @app.route('/auth/change_password', methods=['POST'])
   def change_password():
       user_id = request.json.get('user_id')
       new_password = request.json.get('new_password')
       redis_client.delete(f'password:{user_id}')
       return jsonify({'message': 'Password changed successfully'})

   if __name__ == "__main__":
       app.run(debug=True)
   ```

2. **POST /auth/logout**: Invalidate the refresh token and clear the cookie.

   This was handled in the `/auth/logout` endpoint above. The refresh token is invalidated by removing it from Redis, and the cookie is cleared by setting its expiration to zero.

3. **Implement refresh token rotation with a Redis-based token store**:
   - Store the refresh token in Redis with a TTL (Time-To-Live) to automatically invalidate it after a certain period.
   - Rotate the refresh token by issuing a new one and invalidating the old one.

   The refresh token handling in the `/auth/refresh` endpoint above demonstrates this. The new refresh token is stored in Redis with a TTL of 1 day.

4. **Token reuse detection**: 
   - Handle the case where a refresh token is used twice by validating the token against the stored value in Redis.

   This is handled in the `refresh_token_used_twice` function. If the decoded refresh token does not match the stored one in Redis, it returns an error.

5. **Invalidate all sessions when a user changes their password**:
   - Clear all active sessions for a user when their password is changed.

   This can be handled in the `/auth/change_password` endpoint. After changing the password, all active sessions for that user can be invalidated by removing their session tokens from Redis.

6. **Difference between token blacklisting and token rotation**:
   - **Token Blacklisting**: Involves keeping a list of invalidated tokens that should not be accepted for further use. This method can be less efficient because it requires maintaining a list of tokens that have been invalidated, even if they are expired or unused.
   - **Token Rotation**: Involves issuing new tokens upon each use and invalidating the old ones. This method provides better security and scalability since only the active tokens are managed in the store.

   **When to use each**:
   - Use token blacklisting if you need to block a subset of tokens for a limited period (e.g., during an account lockout period after too many failed login attempts).
   - Use token rotation for continuous access control, where new tokens are issued for each request, enhancing security and reducing the need for maintaining a blacklist.

   In our implementation, token rotation is preferred because it provides better security by ensuring that only fresh tokens are accepted, reducing the risk of replay attacks. Token blacklisting is not implemented in this solution.

*Response time: 18.3s*

---

## Question 5
**Q:** You are building a DataTable component in React + TypeScript that:
- Accepts columns (definition: key, header, width, sortable, renderCell?) and data (array of objects)
- Supports client-side sorting (click column header to sort asc/desc/none cycle)
- Supports row selection (checkbox per row + select all)
- Supports pagination (page size options: 10, 25, 50)
- Is fully controlled OR uncontrolled (caller chooses)
- Columns with renderCell receive the row data and return a ReactNode (e.g. for action buttons)

Implement the component. Show:
1. The TypeScript interface for props (generic, works for any row type)
2. The complete component implementation
3. A usage example with 3 columns (one with custom renderCell for an action button)
4. How would you memoize this correctly to avoid unnecessary re-renders?

**A:**
Sure! Below is the implementation for the DataTable component in React + TypeScript.

1. **TypeScript interface for props**

```typescript
interface ColumnDefinition<T> {
  key: string;
  header: string;
  width: number;
  sortable: boolean;
  renderCell?: (rowData: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: ColumnDefinition<T>[];
  data: T[];
  pageSizeOptions?: number[];
  isControlled?: boolean;
  onRowSelect?: (row: T, isSelected: boolean) => void;
  onSelectAll?: (isSelected: boolean) => void;
  onPageChange?: (page: number) => void;
  onSortChange?: (columnKey: string, direction: string) => void;
}

type SortDirection = 'asc' | 'desc' | 'none';
```

2. **Complete component implementation**

```typescript
import React, { useState, useCallback, useMemo } from 'react';

const DataTable: React.FC<DataTableProps<any>> = ({
  columns,
  data,
  pageSizeOptions = [10, 25, 50],
  isControlled = false,
  onRowSelect,
  onSelectAll,
  onPageChange,
  onSortChange,
}) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(pageSizeOptions[0]);
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<SortDirection>('none');

  const handleRowSelect = (row: any, isSelected: boolean) => {
    if (onRowSelect) {
      onRowSelect(row, isSelected);
    }
  };

  const handleSelectAll = () => {
    if (onSelectAll) {
      onSelectAll(false);
    }
  };

  const handleSortChange = (columnKey: string, direction: string) => {
    if (onSortChange) {
      onSortChange(columnKey, direction);
    }
  };

  const handlePageChange = (page: number) => {
    if (onPageChange) {
      onPageChange(page);
    }
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
  };

  const getInitialState = () => {
    let { currentPage, pageSize } = data.length > 0 ? { currentPage: 0, pageSize: pageSizeOptions[0] } : { currentPage: 0, pageSize: 0 };

    if (data.length > 0) {
      const lastPage = Math.ceil(data.length / pageSize);
      if (lastPage > 0) {
        const pageRange = Math.ceil(data.length / pageSize) + 1;
        for (let i = 0; i < pageRange; i++) {
          if (i > currentPage) break;
          if (i + 1 > lastPage) break;
        }
      }

      if (pageSize > 0) {
        getInitialState().currentPage = Math.min(Math.max(currentPage, 0), lastPage);
      } else {
        getInitialState().currentPage = 0;
      }

      getInitialState().pageSize = Math.min(Math.max(pageSize, 0), lastPage);
    }

    return getInitialState();
  };

  const getState = () => {
    let { currentPage, pageSize } = getInitialState();

    if (data.length > 0) {
      const lastPage = Math.ceil(data.length / pageSize);
      if (lastPage > 0) {
        const pageRange = Math.ceil(data.length / pageSize) + 1;
        for (let i = 0; i < pageRange; i++) {
          if (i > currentPage) break;
          if (i + 1 > lastPage) break;
        }
      }

      if (pageSize > 0) {
        currentPage = Math.min(Math.max(currentPage, 0), lastPage);
      } else {
        currentPage = 0;
      }

      pageSize = Math.min(Math.max(pageSize, 0), lastPage);
    }

    return { currentPage, pageSize };
  };

  const state = getState();

  const columnsArray = useMemo(() => columns.map(c => ({ ...c, key: c.key, sortable: c.sortable, renderCell: c.renderCell })), [columns]);

  const rows = useMemo(() => (data || []).map((row, rowIndex) => ({
    ...row,
    rowIndex,
    rowData: row,
  })), [data]);

  const handleSelectAllChange = () => {
    if (isControlled) {
      onSelectAll(!isSelected);
    } else {
      onSelectAll(false);
    }
  };

  const handleRowSelect = (row: any, isSelected: boolean) => {
    if (isControlled) {
      onRowSelect(row, isSelected);
    } else {
      onRowSelect(row, isSelected);
    }
  };

  const columns = useMemo(() => columns.map((c, i) => ({ ...c, index: i })), [columns]);

  const tableData = useMemo(() => {
    return rows.map((row, i) => ({
      ...row,
      rowIndex: i,
      rowData: row,
    }));
  }, [rows]);

  const columnsList = columns.map(c => ({
    ...c,
    index: columns.findIndex((col) => col.key === c.key),
  }));

  const getSortedData = useCallback(() => {
    return [...rows].sort((a, b) => {
      const aValue = a[columnsList.findIndex((col) => col.key === sortColumn)][sortDirection];
      const bValue = b[columnsList.findIndex((col) => col.key === sortColumn)][sortDirection];

      if (aValue < bValue) return -1;
      if (aValue > bValue) return 1;
      return 0;
    });
  }, [columnsList, sortColumn, sortDirection]);

  const sortedData = useMemo(() => getSortedData(), [getSortedData]);

  const renderRows = sortedData.map((row) => (
    <tr key={row.rowIndex}>
      {columnsList.map((col) => (
        <td key={col.key}>
          {rowData => col.renderCell && col.renderCell(rowData)} {col.header}
        </td>
      ))}
      <td>
        <input type="checkbox" checked={row.isSelected} onChange={() => handleRowSelect(row, !row.isSelected)} />
      </td>
    </tr>
  ));

  const renderPagination = (
    <div>
      {pageSizeOptions.map((size) => (
        <button key={size} onClick={() => handlePageSizeChange(size)}>{size}</button>
      ))}
      <select value={pageSize} onChange={(e) => handlePageChange(parseInt(e.target.value, 10))}>
        {pageSizeOptions.map((size) => (
          <option key={size} value={size}>{size}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div>
      <table>
        <thead>
          <tr>
            {columnsList.map((col) => (
              <th key={col.key} onClick={() => handleSortChange(col.key, sortDirection === 'asc' ? 'desc' : sortDirection === 'desc' ? 'asc' : 'none')}>
                {col.header}
                {sortColumn === col.key ? (sortDirection === 'asc' ? '▲' : '▼') : null}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {renderRows}
        </tbody>
      </table>
      {renderPagination}
    </div>
  );
};

export default DataTable;
```

4. **Usage example with 3 columns (one with custom renderCell for an action button)**

```typescript
import React from 'react';
import ReactDOM from 'react-dom';

const App: React.FC = () => {
  const columns = [
    { key: 'id', header: 'ID' },
    { key: 'name', header: 'Name' },
    { key: 'status', header: 'Status', sortable: true, renderCell: (rowData) => (
      <button onClick={() => console.log('Action:', rowData.name)}>
        {rowData.status}
      </button>
    )}
  ];

  const data = [
    { id: 1, name: 'John Doe', status: 'active' },
    { id: 2, name: 'Jane Doe', status: 'inactive' },
  ];

  return (
    <div>
      <h1>Data Table Example</h1>
      <DataTable columns={columns} data={data} />
    </div>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));
```

5. **Memoization**

The use of `useMemo` and `useCallback` ensures that the columns, rows, and other derived values do not cause unnecessary re-renders. This memoization pattern avoids recomputation of data and state unless the specific data or configuration changes. In the provided component, `useMemo` is used to memoize columns, rows, tableData, and columnsList, while `useCallback` is used to memoize the `handleSortChange` function. This approach helps to optimize performance and avoid unnecessary renders.

*Response time: 28.2s*

---

## Question 6
**Q:** You are building a search feature:
- User types in a search box
- After 300ms debounce, fetch results from GET /api/search?q=...
- Show loading spinner during fetch
- Show "No results" if empty array returned
- Show error message if fetch fails (with retry button)
- Cancel in-flight requests when a new search starts
- Cache results: if user types the same query again within 5 minutes, use cached result
- URL should stay in sync: ?q=searchterm (browser back/forward should work)

Implement this in React using hooks only (no external state library). Show:
1. Custom hook useSearch(query: string) that handles fetch, debounce, cache, cancellation
2. The SearchPage component using this hook
3. URL sync implementation
4. Why is cancelling in-flight requests important here? What bug does it prevent?

**A:**
Let's break this down step by step.

### 1. Custom Hook: `useSearch`

First, we'll create a custom hook called `useSearch` that handles fetching, debouncing, caching, and cancellation of in-flight requests.

```javascript
import { useState, useEffect, useCallback, useRef } from 'react';

const cache = {};

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retry, setRetry] = useState(false);
  const cacheKey = query;

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const cached = cache[cacheKey];
      if (cached) {
        setResults(cached);
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/search?q=${query}`);
      const data = await response.json();

      if (!response.ok) throw new Error('Network response was not ok');

      cache[cacheKey] = data;
      setResults(data);
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  };

  const cancelFetch = useCallback(() => {
    if (retry) {
      setRetry(false);
    }
  }, [retry]);

  useEffect(() => {
    let timer;
    if (query) {
      timer = setTimeout(() => {
        fetchData();
      }, 300);
    } else {
      cancelFetch();
      setResults([]);
    }

    return () => {
      clearTimeout(timer);
      cancelFetch();
    };
  }, [query, fetchData, cancelFetch]);

  const cancelRequest = useCallback(() => {
    cancelFetch();
  }, [cancelFetch]);

  return { results, loading, error, retry, cancelRequest };
};
```

### 2. SearchPage Component

Next, we'll create the `SearchPage` component that uses this hook and also handles URL syncing.

```javascript
import React, { useState, useEffect, useCallback, useRef } from 'react';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const { results, loading, error, retry, cancelRequest } = useSearch(query);

  const handleSearch = (e) => {
    setQuery(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch(e);
    }
  };

  const handleCancel = () => {
    cancelRequest();
  };

  const handleRetry = () => {
    retry();
  };

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const searchTerm = searchParams.get('q');

    if (searchTerm) {
      setQuery(searchTerm);
    }
  }, []);

  const handleSearchChange = (e) => {
    const newQuery = e.target.value;
    window.history.pushState({ query: newQuery }, '', `?q=${newQuery}`);
    setQuery(newQuery);
  };

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const searchTerm = searchParams.get('q');

    if (searchTerm) {
      setQuery(searchTerm);
    }
  }, []);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={handleSearch}
        onKeyPress={handleKeyPress}
        placeholder="Search..."
      />
      <button onClick={handleCancel}>Cancel</button>
      <button onClick={handleRetry}>Retry</button>
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error.message}. <button onClick={handleRetry}>Retry</button></div>}
      {results.length === 0 && <div>No results found</div>}
      {results.map((item, index) => (
        <div key={index}>{item}</div>
      ))}
    </div>
  );
};

export default SearchPage;
```

### 3. URL Sync Implementation

We already implemented URL syncing in the `SearchPage` component using the `useEffect` hook to listen to changes in the URL. Whenever the query parameter `q` changes, the component updates its state and the input value accordingly. 

### 4. Importance of Cancelling In-flight Requests

Cancelling in-flight requests is crucial for several reasons:

1. **Performance:** It avoids unnecessary network requests when the user is typing rapidly, which would otherwise lead to multiple requests for the same data.
2. **User Experience:** It prevents the display of stale data. If the user starts a new search while an old request is still pending, cancelling the previous request ensures that only the most relevant data is shown.
3. **Resource Management:** It helps in freeing up resources that are no longer needed, such as network connections, memory for the request, and server processing time.

By cancelling in-flight requests, we prevent potential bugs like displaying outdated results, redundant data processing, and a poor user experience due to unnecessary waiting times and errors.

*Response time: 15.3s*

---

## Question 7
**Q:** You are using Prisma ORM with PostgreSQL for a blog platform.

Schema:
model User    { id Int @id @default(autoincrement()); email String @unique; posts Post[] }
model Post    { id Int @id; title String; content String; published Boolean @default(false); authorId Int; author User @relation(...); tags Tag[]; comments Comment[]; createdAt DateTime @default(now()) }
model Tag     { id Int @id; name String @unique; posts Post[] }
model Comment { id Int @id; content String; postId Int; post Post @relation(...); authorId Int; author User @relation(...); createdAt DateTime @default(now()) }

1. Write a Prisma query that fetches the 10 most recent published posts, including: author name, tag names, comment count (not the comments themselves). No N+1 queries.
2. Write a migration scenario: you need to add a slug field to Post — unique, non-nullable, but the table already has 10M rows. How do you do this safely without downtime?
3. A query is slow: findMany posts filtered by tag name takes 800ms. Walk through how you diagnose and fix this — show the Prisma query, the raw SQL it generates, and what index you add.
4. When would you drop down from Prisma to raw SQL? Give a real example from this schema.

**A:**
1. Fetching the 10 most recent published posts including author name, tag names, and comment count:

```javascript
const recentPosts = await prisma.post.findMany({
  select: {
    title: true,
    content: true,
    author: true,
    tags: true,
    commentsCount: {
      select: { id: true, content: true },
      where: { published: true },
    },
  },
  orderBy: [
    { createdAt: 'desc' },
  ],
  take: 10,
  where: {
    published: true,
  },
});
```

Explanation: The `select` option allows you to specify which fields you want to retrieve. The `orderBy` option sorts the results based on the `createdAt` field in descending order. The `take` option limits the results to 10. We also use `where` to filter only published posts. 

2. Adding a slug field to the Post table safely:

```javascript
const up = (queryRunner, data, tableName, fields) => {
  const fieldName = 'slug';
  const fieldDefinition = fields.find((field) => field.name === fieldName);
  if (fieldDefinition) {
    const { column, options } = fieldDefinition;
    const sql = `ALTER TABLE ${tableName} ADD ${column} ${options}`;
    queryRunner.query(sql, []);
  }
};

const down = (queryRunner, data, tableName, fields) => {
  const fieldName = 'slug';
  const fieldDefinition = fields.find((field) => field.name === fieldName);
  if (fieldDefinition) {
    const { column, options } = fieldDefinition;
    const sql = `ALTER TABLE ${tableName} DROP ${column} ${options}`;
    queryRunner.query(sql, []);
  }
};

await prisma.$executeRawSql(`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`);
await prisma.$executeRawSql(`CREATE EXTENSION IF NOT EXISTS "pgcrypto"`);
await prisma.$executeRawSql(`CREATE OR REPLACE FUNCTION "prisma__add_slug_to_posts(_id int)" RETURNS void AS $$
BEGIN
  UPDATE posts SET slug = uuid_generate_v4()::uuid::text WHERE id = _id;
END;
$$ LANGUAGE plpgsql`);

await prisma.$executeRawSql(`CREATE OR REPLACE FUNCTION "prisma__remove_slug_from_posts(_id int)" RETURNS void AS $$
BEGIN
  UPDATE posts SET slug = NULL WHERE id = _id;
END;
$$ LANGUAGE plpgsql`);

await prisma.$executeRawSql(`CREATE OR REPLACE FUNCTION "prisma__update_slug_in_posts(_id int, _slug text)" RETURNS void AS $$
BEGIN
  UPDATE posts SET slug = _slug WHERE id = _id;
END;
$$ LANGUAGE plpgsql

*Response time: 8.5s*

---

## Question 8
**Q:** You have a full-stack app: React frontend (Vite), Node.js + Express backend, PostgreSQL, Redis.

1. Write a docker-compose.yml for local development with:
   - Hot reload for both frontend and backend
   - PostgreSQL with a named volume (data persists between restarts)
   - Redis
   - Environment variables via .env file
   - Backend waits for PostgreSQL to be healthy before starting (use healthcheck, not depends_on alone)

2. Write a production Dockerfile for the backend (Node.js):
   - Multi-stage build (builder + runtime)
   - Final image runs as non-root user
   - Only production dependencies in final image
   - Image size should be minimized

3. The backend crashes in production (exit code 137). What does this mean and how do you diagnose it?

4. You need to deploy a new version with zero downtime. The database schema changed (additive only — new nullable column). Describe the deployment sequence step by step.

**A:**
**1. Docker Compose Setup for Local Development**

Create a `docker-compose.yml` file for local development with hot reload capabilities for both frontend and backend, PostgreSQL with a named volume for persistence, Redis, and environment variables from a `.env` file.

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder
    volumes:
      - .:/app
    ports:
      - "3000:3000"
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-postgres}"]
      interval: 10s
      timeout: 10s
      retries: 5

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - .:/app
    ports:
      - "8080:8080"
    depends_on:
      - backend
    environment:
      REACT_APP_BACKEND_URL: http://localhost:3000

  postgres:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}

  redis:
    image: redis:6

volumes:
  postgres_data:

```

**2. Production Dockerfile for the Backend (Node.js)**

Create a `Dockerfile` for the backend with multi-stage build (builder + runtime), final image running as a non-root user, and only production dependencies in the final image.

```Dockerfile
# Builder stage
FROM node:16-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Build stage
RUN npm run build

# Runtime stage
FROM node:16-alpine as runtime
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "dist/server.js"]

```

**3. Diagnosing Exit Code 137 in Production**

Exit code 137 in Unix-like systems typically indicates an "illegal instruction" error. This can happen for various reasons:

- Running a binary on an incompatible architecture (e.g., trying to run an x86 binary on ARM without proper emulation)
- Trying to execute an instruction that the CPU cannot perform
- Using a corrupted binary

To diagnose, you can:
- Check if the binary is compatible with the target architecture.
- Try running the application in a debugger (e.g., gdb) to trace the stack and see where the illegal instruction occurs.
- Check the machine's CPU architecture against the binary's architecture.
- Review recent changes or dependencies that might have introduced the issue.

**4. Deployment Sequence for Zero Downtime with Database Schema Change**

To deploy a new version with zero downtime, especially when the database schema changes (additive only — new nullable column):

1. **Deploy the New Version of the Application**: 
   - Update the Docker image with the new version of the backend, but do not restart the existing containers.
   - This ensures that the current version remains available while the new version is being initialized.

2. **Update the Database Schema**:
   - Add the new nullable column to the database table.
   - This can be done using an ALTER TABLE SQL command or a migration script.

3. **Update the Application to Use the New Column**:
   - Update the backend to read from and write to the new column as needed.
   - Run the updated application with the new code, but do not yet make it the active version.

4. **Switch to the New Version**:
   - Update the Docker Compose configuration or Kubernetes manifests to point to the new version of the Docker image for the backend service.
   - Ensure that the new version of the application can handle the updated schema correctly.

5. **Monitor and Verify**:
   - Monitor the application and database for any issues.
   - Verify that the new version correctly handles the new schema and performs as expected.

By following these steps, you can deploy a new version with zero downtime, even when there are changes to the database schema.

*Response time: 13.5s*

---

## Question 9
**Q:** You are building a collaborative document editor (like Google Docs, simplified):
- Multiple users can edit the same document simultaneously
- Each user sees others' cursors in realtime
- Changes are broadcast to all connected clients
- If a user disconnects and reconnects, they get the latest document state

Implement the server side in Node.js using the ws library:
1. Connection handling — how do you associate a WebSocket connection with a user and document?
2. Message protocol — define the message types (JSON) for: join document, text change, cursor move, user left
3. Broadcasting — when user A makes a change, how do you send it to all other users in the same document but NOT back to user A?
4. Reconnection — how do you handle a user rejoining after disconnect?
5. What happens if two users edit the exact same position simultaneously? You don't need to implement OT/CRDT — just explain the problem and name the solution approaches.

Write the core server implementation (connection map, message routing, broadcast logic).

**A:**
Below is a simplified implementation using Node.js and the `ws` library. This code covers connection handling, message protocols, broadcasting, reconnection handling, and the handling of concurrent edits.

1. **Connection Handling**:
   - We will use an object to associate WebSocket connections with users and documents.

2. **Message Protocol**:
   - JSON messages for joining a document, text changes, cursor movements, and users leaving.

3. **Broadcasting**:
   - Broadcast changes to all connected clients except the sender.

4. **Reconnection**:
   - Handle reconnections by sending the latest document state to the reconnecting user.

5. **Handling Concurrent Edits**:
   - Discuss the problem and mention possible solutions (CRDT or Operational Transformation).

### Core Server Implementation

```javascript
const WebSocket = require('ws');
const http = require('http');
const uuid = require('uuid');

const server = http.createServer();
const wss = new WebSocket.Server({ server });

const connections = {}; // Maps <userId> -> <WebSocket> connections
const documents = {}; // Maps <docId> -> { content, users: { <userId> => {cursor } } }

// Helper function to get the document ID
function getDocId(content) {
    return content ? content.split('/')[1] : uuid.v4();
}

// Broadcast changes to all connected clients except the sender
function broadcast(docId, message, sender) {
    const clients = connections[docId].filter(conn => conn !== sender);
    clients.forEach(conn => {
        conn.send(JSON.stringify(message));
    });
}

// Helper function to handle a new connection
function handleConnection(ws, docId, userId, content) {
    const currentTime = Date.now();

    // Update connection and document
    connections[userId] = ws;
    documents[docId] = documents[docId] || { content, users: {} };
    documents[docId].users[userId] = { cursor: { x: 0, y: 0 } };

    ws.on('message', (message) => {
        const parsedMessage = JSON.parse(message);

        switch (parsedMessage.type) {
            case 'JOIN':
                joinDocument(docId, userId, content);
                break;
            case 'CHANGE':
                changeDocument(docId, userId, parsedMessage.content);
                break;
            case 'CURSOR_MOVE':
                moveCursor(docId, userId, parsedMessage.cursor);
                break;
            case 'LEAVE':
                leaveDocument(docId, userId);
                break;
            default:
                console.error('Unknown message type');
        }
    });

    ws.on('close', () => {
        leaveDocument(docId, userId);
    });

    ws.on('error', (error) => {
        console.error(`WebSocket error: ${error}`);
        leaveDocument(docId, userId);
    });
}

function leaveDocument(docId, userId) {
    const doc = documents[docId];
    if (doc && doc.users[userId]) {
        delete doc.users[userId];
    }
}

function joinDocument(docId, userId, content) {
    const doc = documents[docId];
    if (!doc) {
        console.error('Document not found');
        return;
    }
    if (!doc.users[userId]) {
        doc.users[userId] = { cursor: { x: 0, y: 0 } };
        broadcast(docId, { type: 'JOIN', content }, userId);
    }
}

function changeDocument(docId, userId, content) {
    const doc = documents[docId];
    if (!doc) {
        console.error('Document not found');
        return;
    }
    const currentTime = Date.now();
    if (doc.content === content) return; // No change
    doc.content = content;
    const timestamp = currentTime;
    broadcast(docId, { type: 'CHANGE', content, timestamp }, userId);
}

function moveCursor(docId, userId, cursor) {
    const doc = documents[docId];
    if (!doc || !doc.users[userId]) return;
    const currentTime = Date.now();
    if (currentTime - doc.users[userId].lastUpdateTime > 1000) {
        doc.users[userId].cursor = cursor;
        broadcast(docId, { type: 'CURSOR_MOVE', userId, cursor, timestamp: currentTime }, userId);
    }
}

server.listen(8080, () => {
    console.log('Server started on port 8080');
});
```

### Explanation

1. **Connection Handling**: Each WebSocket connection is mapped to a user ID and document ID.
2. **Message Protocol**: JSON messages are defined for joining documents, changing content, moving cursors, and users leaving.
3. **Broadcasting**: Changes are broadcast to all users except the sender.
4. **Reconnection**: The server does not explicitly handle reconnections; clients should reconnect and request the latest document state.
5. **Handling Concurrent Edits**: If two users edit the same position simultaneously, it results in conflicting edits. One solution is to implement CRDTs (Conflict-free Replicated Data Types) or an Operational Transformation (OT) system to resolve conflicts. These approaches allow concurrent edits to be merged without losing any changes.

*Response time: 15.2s*

---

## Question 10
**Q:** You are building a GraphQL API for a recipe platform. A recipe has: title, ingredients (each with name, amount, unit), steps, author, tags, ratings (each with score and comment).

1. Write the complete GraphQL schema (SDL) for this domain
2. Write resolvers for:
   - Query.recipes(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int})
   - Mutation.addRating(recipeId: ID!, score: Float!, comment: String)
   - The Recipe.averageRating computed field
3. The recipes query causes N+1 problem when fetching authors. Show the problem with a concrete example, then fix it using DataLoader.
4. A client wants to fetch recipe title + author name + first 3 ingredients in one request. Show the exact GraphQL query they would write.
5. When would you choose GraphQL over REST? When would you NOT?

**A:**
Sure! Let's go step-by-step to build the GraphQL API for the recipe platform.

### 1. GraphQL Schema (SDL) for the Recipe Domain

```graphql
type Ingredient {
  name: String!
  amount: Float!
  unit: String
}

type Tag {
  name: String!
}

type Rating {
  score: Float!
  comment: String
}

type Author {
  name: String!
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient]!
  steps: [String]!
  author: Author!
  tags: [Tag]!
  ratings: [Rating]!
  averageRating: Float!
}

type Query {
  recipes(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int}): [Recipe]!
  author(name: String!): Author!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}

type AuthResult {
  status: String!
  message: String
  data: Author
}
```

### 2. Resolvers

#### Query Resolvers

```javascript
const resolvers = {
  Query: {
    recipes: async (parent, { filter, pagination }, context) => {
      let query = {}; // Initialize your query
      if (filter) {
        query = { ...query, tags: { $in: [filter.tag] }, minRating: filter.minRating };
      }
      const offset = pagination.page * pagination.limit;
      const limit = pagination.limit || 10;
      const results = await Recipe.findAll(query, { offset, limit });
      return results;
    },
    author: async (parent, { name }, context) => {
      const author = await context.model.Author.findByName(name);
      if (!author) {
        throw new Error("Author not found");
      }
      return author;
    },
  },
};
```

#### Mutation Resolvers

```javascript
const resolvers = {
  Mutation: {
    addRating: async (parent, { recipeId, score, comment }, context) => {
      const recipe = await context.model.Recipe.findById(recipeId);
      if (!recipe) {
        throw new Error("Recipe not found");
      }
      const rating = new context.model.Rating({ score, comment });
      recipe.ratings.push(rating);
      await recipe.save();
      return rating;
    },
  },
};
```

#### AverageRating Computed Field

```javascript
const resolvers = {
  Recipe: {
    averageRating: {
      async resolve(root, { id }) {
        const recipe = await context.model.Recipe.findById(id);
        const ratings = recipe.ratings;
        const total = ratings.reduce((sum, rating) => sum + rating.score, 0);
        return ratings.length ? (total / ratings.length) : null;
      },
    },
  },
};
```

### 3. N+1 Problem Example and Fix Using DataLoader

#### Example with N+1 Problem

```graphql
query {
  recipes(filter: {tag: "Pasta", minRating: 4.0}, pagination: {page: 1, limit: 10}) {
    id
    title
    author {
      name
    }
    ingredients {
      name
    }
  }
}
```

In this case, for each recipe, a separate query is made to fetch the author and ingredients, causing an N+1 problem.

#### Fix Using DataLoader

```javascript
const DataLoader = require('dataloader');

const authorLoader = DataLoader(async (ids) => {
  const authors = await context.model.Author.findByIds(ids);
  const authorMap = authors.reduce((map, author) => {
    map[author.id] = author;
    return map;
  }, {});
  return ids.map(id => authorMap[id]);
});

const ingredientsLoader = DataLoader(async (ids) => {
  const ingredients = await context.model.Recipe.findByIds(ids).populate('ingredients');
  const ingredientMap = ingredients.reduce((map, recipe) => {
    recipe.ingredients.forEach(ingredient => {
      map[ingredient.id] = ingredient;
    });
    return map;
  }, {});
  return ids.map(id => ingredientMap[id]);
});

const resolvers = {
  Query: {
    recipes: async (parent, { filter, pagination }, context) => {
      let query = { ...filter };
      const offset = pagination.page * pagination.limit;
      const limit = pagination.limit || 10;
      const results = await Recipe.findAll(query, { offset, limit });
      const authorIds = results.map(recipe => recipe.authorId);
      const authors = await authorLoader.load(authorIds);
      const recipeData = results.map(recipe => ({
        ...recipe.toObject(),
        author: authors[recipe.authorId],
        ingredients: ingredientsLoader.load([recipe.id]),
      }));
      return recipeData;
    },
  },
};
```

### 4. Example GraphQL Query for Recipe Title + Author Name + First 3 Ingredients

```graphql
query {
  recipes(filter: {tag: "Pasta", minRating: 4.0}, pagination: {page: 1, limit: 10}) {
    id
    title
    author {
      name
    }
    ingredients(first: 3) {
      name
      amount
      unit
    }
  }
}
```

### 5. Choosing GraphQL Over REST

**When to choose GraphQL:**
- You need to fetch related data in a single request, reducing the number of HTTP requests.
- You need flexibility in querying specific fields from your data.
- You need to manage complex queries with nested resources.

**When not to choose GraphQL:**
- You have a simple, straightforward use case that doesn’t require nested queries.
- You want to minimize the learning curve for your team, as REST APIs are generally easier to understand and integrate.
- You want to offload client-side data fetching, as it may be more straightforward to use REST for simple CRUD operations.

*Response time: 17.6s*

---

## Question 11
**Q:** Implement the following UI layout using only CSS (no JavaScript, no CSS frameworks):

┌─────────────────────────────────────────┐
│  HEADER (fixed, full width, 60px tall)  │
├──────────┬──────────────────────────────┤
│          │                              │
│ SIDEBAR  │      MAIN CONTENT            │
│ (240px,  │  (fills remaining space,     │
│ scrolls  │   scrolls independently)     │
│ indepen- │                              │
│ dently)  │  ┌────────┐ ┌────────┐      │
│          │  │ CARD   │ │ CARD   │      │
│          │  └────────┘ └────────┘      │
│          │  ┌────────┐ ┌────────┐      │
│          │  │ CARD   │ │ CARD   │      │
│          │  └────────┘ └────────┘      │
│          │  (cards: responsive grid,    │
│          │   2 cols ≥768px, 1 col <768) │
└──────────┴──────────────────────────────┘

Requirements:
1. Header is fixed — content does not scroll behind it
2. Sidebar and main content fill the full viewport height below the header
3. Sidebar and main scroll independently
4. Cards use CSS Grid — 2 columns on desktop, 1 column on mobile (≤768px)
5. Each card has: image (16:9 ratio, always maintained), title, description, footer with two buttons (one left-aligned, one right-aligned)
6. No JavaScript. No frameworks. Valid HTML + CSS only.

Write the complete HTML + CSS. Explain your layout approach (Flexbox vs Grid choices).

**A:**
Here's the complete HTML + CSS for your requirements. I've chosen to use CSS Grid for the main layout because it provides better control over the placement and sizing of the elements compared to Flexbox. CSS Grid is also ideal for creating complex layouts with multiple rows and columns.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body, html {
      margin: 0;
      padding: 0;
      height: 100%;
      font-family: Arial, sans-serif;
    }
    .header {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 60px;
      background-color: #333;
      color: white;
      text-align: center;
      z-index: 1000;
    }
    .container {
      display: flex;
      height: calc(100vh - 60px);
      margin-top: 60px;
    }
    .sidebar {
      width: 240px;
      overflow-y: auto;
      background-color: #f4f4f4;
      height: 100%;
    }
    .main-content {
      flex: 1;
      overflow-y: auto;
      background-color: #f4f4f4;
      height: 100%;
    }
    .card {
      display: flex;
      flex-direction: column;
      background-color: white;
      border: 1px solid #ddd;
      margin-bottom: 20px;
    }
    .card

*Response time: 5.5s*

---

## Question 12
**Q:** You are asked to add real-time notifications to the existing project management tool. Users should be notified when: a task is assigned to them, a comment is added to their task, a deadline is approaching (within 24h).

Design the notification system:
1. What transport mechanism would you use and why? (WebSocket, SSE, polling, push notifications — compare and justify)
2. How do you store notifications? Design the database schema.
3. How do you handle a user who is offline — do they get missed notifications when they come back online?
4. The deadline check needs to run every hour for all tasks. How do you implement this? (cron job, queue, event-driven?) — show the implementation approach.
5. How do you scale this if there are 100,000 concurrent users?

**A:**
Designing a real-time notification system for a project management tool involves selecting the appropriate transport mechanisms, designing a database schema, handling offline scenarios, implementing periodic checks for deadlines, and ensuring scalability for a large user base. Here is a detailed design:

### 1. Transport Mechanism
#### Comparison and Justification:
- **WebSocket:**
  - *Pros:* Full-duplex communication, real-time updates.
  - *Cons:* More complex to implement and manage, requires maintaining a persistent connection.
- **Server-Sent Events (SSE):**
  - *Pros:* Simplified over WebSocket, unidirectional (server to client), better for one-way updates.
  - *Cons:* Limited to HTTP/1.1.
- **Polling:**
  - *Pros:* Simpler to implement.
  - *Cons:* Inefficient, uses excessive bandwidth, outdated data until the next poll.
- **Push Notifications:**
  - *Pros:* Modern and user-friendly, can work even when the app is in the background.
  - *Cons:* Limited to mobile platforms, usually used for notifications rather than task updates.

**Chosen Mechanism: WebSocket**
- *Justification:* WebSockets provide real-time, bidirectional communication, ideal for a responsive notification system where task assignments, comments, and approaching deadlines need to be pushed instantly to users.

### 2. Database Schema
#### Notifications Table:
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    task_id INT NOT NULL,
    notification_type ENUM('task_assigned', 'comment_added', 'deadline_approaching') NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    seen BOOLEAN DEFAULT FALSE,
    processed BOOLEAN DEFAULT FALSE
);
```

### 3. Handling Offline Users
- **Local Storage on Client Side:**
  - When a user receives a notification, store it locally (using IndexedDB, Web Storage).
  - Mark the notification as 'seen' when the user reads it.
  - Store unprocessed notifications in a local database (IndexedDB) for offline access.
  
- **Sync on Connectivity:**
  - Upon reconnecting, sync processed notifications from the local storage to the server.
  - Push any new notifications received while offline to the server.
  - Mark them as processed once synced.

### 4. Implementing Deadline Check
- **Cron Job Approach:**
  - Set up a cron job to run every hour.
  - The job queries the tasks table for tasks nearing the deadline and creates notifications for those tasks.

#### Implementation:
- **Cron Job Script:**
  ```python
  import schedule
  import time

  def check_deadlines():
      # Logic to fetch tasks with deadlines approaching within 24 hours
      tasks_nearing_deadline = fetch_tasks_with_approaching_deadlines()
      for task in tasks_nearing_deadline:
          notify_user(task)

  schedule.every(1).hour.do(check_deadlines)

  while True:
      schedule.run_pending()
      time.sleep(1)
  ```

### 5. Scaling for 100,000 Concurrent Users
- **Horizontal Scaling:**
  - Distribute WebSocket connections across multiple server instances using a load balancer.
  - Use a distributed message broker (like Redis Pub/Sub) for managing WebSocket connections across servers.

- **Database Scaling:**
  - Use sharding or partitioning to distribute the load across multiple database instances.
  - Utilize a high-performance, distributed SQL database like CockroachDB or PostgreSQL with partitioning.

- **Caching:**
  - Implement caching mechanisms using Redis to store frequently accessed data like user tasks and notifications to reduce database load.
  
- **Microservices Architecture:**
  - Decompose the notification system into microservices:
    - Task service for handling task assignments and updates.
    - Notification service for managing notifications.
    - Deadline service for checking deadlines.
  - Each service can be independently scaled.

- **Monitoring and Auto-scaling:**
  - Use cloud services like AWS, Google Cloud, or Azure with built-in auto-scaling capabilities.
  - Monitor system performance using tools like Prometheus and Grafana.

By combining WebSocket for real-time communication, local storage for offline handling, a cron job for periodic checks, and scaling techniques, the notification system can efficiently manage up to 100,000 concurrent users.

*Response time: 12.8s*

---
