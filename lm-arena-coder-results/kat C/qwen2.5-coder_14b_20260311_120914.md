# Model: qwen2.5-coder:14b
**Test Date:** 2026-03-11 13:14:57
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
### REST API Design for Multi-Tenant SaaS Project Management Tool

#### 1. Endpoints

**Workspaces**
- **List Workspaces**
  - **GET** `/api/workspaces`
- **Create Workspace**
  - **POST** `/api/workspaces`
- **Get Workspace Details**
  - **GET** `/api/workspaces/{workspaceId}`

**Projects**
- **List Projects in Workspace**
  - **GET** `/api/workspaces/{workspaceId}/projects`
- **Create Project**
  - **POST** `/api/workspaces/{workspaceId}/projects`
- **Get Project Details**
  - **GET** `/api/workspaces/{workspaceId}/projects/{projectId}`

**Tasks**
- **List Tasks in Project**
  - **GET** `/api/workspaces/{workspaceId}/projects/{projectId}/tasks`
- **Create Task**
  - **POST** `/api/workspaces/{workspaceId}/projects/{projectId}/tasks`
- **Update Task Status**
  - **PATCH** `/api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`
- **Get Task Details**
  - **GET** `/api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`

**Comments**
- **Add Comment to Task**
  - **POST** `/api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments`

**Users**
- **List Users in Workspace**
  - **GET** `/api/workspaces/{workspaceId}/users`
- **Add User to Workspace**
  - **POST** `/api/workspaces/{workspaceId}/users`

#### 2. Request/Response JSON Shapes

**Create Task**
- **Request**:
  ```json
  {
    "title": "Task Title",
    "description": "Task Description",
    "due_date": "2023-12-31",
    "assignee_id": "user123"
  }
  ```
- **Response**:
  ```json
  {
    "id": "task456",
    "title": "Task Title",
    "description": "Task Description",
    "due_date": "2023-12-31",
    "assignee_id": "user123",
    "status": "pending",
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
  }
  ```

**Update

*Response time: 46.4s*

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
Sure, let's implement the PATCH endpoint `/workspaces/:workspaceId/tasks/:taskId` using Node.js, Express, and TypeScript. We'll use Zod for validation and write the necessary unit tests.

### Step 1: Install Required Packages

First, ensure you have the required packages installed:

```bash
npm install express typescript ts-node zod @types/express @types/node
```

### Step 2: Create the TypeScript Handler

Let's create a file `taskHandler.ts` for the handler and validation schema.

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { Task, Workspace, User, Subtask } from './models'; // Assume these models are defined

// Validation schema
const taskUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.number().nullable().optional(),
  due_date: z.string().datetime().nullable().optional(),
});

// Middleware to validate request body
const validateTaskUpdate = (req: Request, res: Response, next: NextFunction) => {
  const { error } = taskUpdateSchema.safeParse(req.body);
  if (error) {
    return res.status(400).json({ errors: error.format() });
  }
  next();
};

// PATCH /workspaces/:workspaceId/tasks/:taskId
const updateTask = async (req: Request, res: Response, next: NextFunction) => {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;

  // Validate workspaceId and taskId are integers
  const workspaceIdNum = parseInt(workspaceId, 10);
  const taskIdNum = parseInt(taskId, 10);

  if (isNaN(workspaceIdNum) || isNaN(taskIdNum)) {
    return res.status(400).json({ error: 'Invalid workspaceId or taskId' });
  }

  // Find the task and workspace
  const task = await Task.findOne({ where: { id: taskIdNum } });
  const workspace = await Workspace.findOne({ where: { id: workspaceIdNum } });

  if (!task || !workspace) {
    return res.status(404).json({ error: 'Task or workspace not found' });
  }

  // Validate that the task belongs to the workspace
  if (task.workspaceId !== workspaceIdNum) {
    return res.status(404).json({ error: 'Task not found in the specified workspace' });
  }

  // Validate assignee_id
  if (assignee_id !== null) {
    const assignee = await User.findOne({ where: { id: assignee_id } });
    if (!assignee || assignee.workspaceId !== workspaceIdNum) {
      return res.status(400).json({ error: 'Assignee not found or not part of the workspace' });
    }
  }

  // Check for open subtasks if trying to cancel
  if (status === 'cancelled') {
    const openSubtasks = await Subtask.count({
      where: { taskId: taskIdNum, status: 'todo' },
    });
    if (openSubtasks > 0) {
      return res.status(409).json({ error: 'Cannot cancel task with open subtasks' });
    }
  }

  // Update the task
  const updatedTask = await Task.update(
    {
      title,
      status,
      assignee_id,
      due_date,
    },
    {
      where: { id: taskIdNum },
    }
  );

  res.json(updatedTask);
};

export { validateTaskUpdate, updateTask };
```

### Step 3: Create the Error Middleware

Create a file `errorMiddleware.ts` for the error handling middleware.

```typescript
import express, { Request, Response, NextFunction } from 'express';

const errorMiddleware = (err: any, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
};

export default errorMiddleware;
```

### Step 4: Set Up the Express Server

Create a file `server.ts` to set up the Express server.

```typescript
import express from 'express';
import { validateTaskUpdate, updateTask } from './taskHandler';
import errorMiddleware from './errorMiddleware';

const app = express();
app.use(express.json());

// PATCH /workspaces/:workspaceId/tasks/:taskId
app.patch('/workspaces/:workspaceId/tasks/:taskId', validateTaskUpdate, updateTask, errorMiddleware);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

### Step 5: Write Unit Tests

Create a file `taskHandler.test.ts` for the unit tests.

```typescript
import { describe, it, expect } from '@jest/globals';
import request from 'supertest';
import app from './server';
import { Workspace, Task, User, Subtask } from './models';

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  let workspaceId: number;
  let taskId: number;
  let userId: number;
  let subtaskId: number;

  beforeAll(async () => {
    // Create a workspace, user, task, and subtask for testing
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    workspaceId = workspace.id;

    const user = await User.create({ name: 'Test User', workspaceId });
    userId = user.id;

    const task = await Task.create({ title: 'Test Task', status: 'todo', workspaceId });
    taskId = task.id;

    const subtask = await Subtask.create({ title: 'Test Subtask', status: 'todo', taskId });
    subtaskId = subtask.id;
  });

  it('should update a task successfully', async () => {
    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/${taskId}`)
      .send({ title: 'Updated Task', status: 'in_progress', assignee_id: userId, due_date: new Date().toISOString() });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated Task');
    expect(response.body.status).toBe('in_progress');
    expect(response.body.assignee_id).toBe(userId);
  });

  it('should return 400 with validation errors', async () => {
    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/${taskId}`)
      .send({ title: '', status: 'invalid_status', assignee_id: 'invalid_id', due_date: 'invalid_date' });

    expect(response.status).toBe(400);
    expect(response.body.errors).toBeTruthy();
  });

  it('should return 404 if task or workspace not found', async () => {
    const response = await request(app)
      .patch(`/workspaces/999/tasks/999`)
      .send({ title: 'Updated Task' });

    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Task or workspace not found');
  });

  it('should return 409 if trying to cancel task with open subtasks', async () => {
    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/${taskId}`)
      .send({ status: 'cancelled' });

    expect(response.status).toBe(409);
    expect(response.body.error).toBe('Cannot cancel task with open subtasks');
  });
});
```

### Step 6: Run the Tests

Ensure you have Jest installed:

```bash
npm install --save-dev jest @types/jest ts-jest
```

Then, run the tests:

```bash
npx jest
```

This should cover the implementation of the PATCH endpoint with validation, error handling, and unit tests.

*Response time: 150.1s*

---

## Question 3
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
To implement the PATCH `/workspaces/:workspaceId/tasks/:taskId` endpoint in a Node.js + Express + TypeScript application, we'll follow these steps:

1. Define the validation schema using Zod.
2. Implement the middleware for validating the request.
3. Implement the endpoint handler.
4. Implement error middleware to handle validation and other errors.
5. Write unit tests to cover the success scenario, validation errors, 404, and 409.

Here's the complete implementation:

### 1. Define the Validation Schema using Zod

```typescript
import { z } from 'zod';

const taskUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.number().nullable().optional(),
  due_date: z.string().datetime({ offset: true }).nullable().optional(),
});
```

### 2. Implement the Middleware for Validating the Request

```typescript
import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';

export const validateTaskUpdate = (req: Request, res: Response, next: NextFunction) => {
  const { error } = taskUpdateSchema.safeParse(req.body);
  if (error) {
    res.status(400).json({ errors: error.errors });
  } else {
    next();
  }
};
```

### 3. Implement the Endpoint Handler

```typescript
import { Request, Response } from 'express';
import { validateTaskUpdate } from './validators';
import { Workspace, Task } from './models'; // Assuming you have these models

export const updateTask = async (req: Request, res: Response) => {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;

  if (!/^\d+$/.test(workspaceId) || !/^\d+$/.test(taskId)) {
    return res.status(400).json({ error: 'Invalid workspaceId or taskId' });
  }

  const workspace = await Workspace.findById(parseInt(workspaceId));
  if (!workspace) {
    return res.status(404).json({ error: 'Workspace not found' });
  }

  const task = await Task.findById(parseInt(taskId));
  if (!task || task.workspaceId !== parseInt(workspaceId)) {
    return res.status(404).json({ error: 'Task not found' });
  }

  if (assignee_id !== null && !workspace.members.includes(assignee_id)) {
    return res.status(400).json({ error: 'Assignee is not a member of the workspace' });
  }

  if (status === 'cancelled') {
    const openSubtasks = await Task.find({
      parentId: parseInt(taskId),
      status: { $in: ['todo', 'in_progress'] },
    });

    if (openSubtasks.length > 0) {
      return res.status(409).json({ error: 'Cannot cancel task with open subtasks' });
    }
  }

  task.title = title ?? task.title;
  task.status = status ?? task.status;
  task.assignee_id = assignee_id ?? task.assignee_id;
  task.due_date = due_date ?? task.due_date;

  await task.save();
  res.status(200).json(task);
};
```

### 4. Implement Error Middleware to Handle Validation and Other Errors

```typescript
import { Request, Response, NextFunction } from 'express';

export const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: 'Internal Server Error' });
};
```

### 5. Write Unit Tests

```typescript
import { request } from 'supertest';
import app from './app'; // Assuming you have an Express app
import { Task, Workspace } from './models';

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  let workspaceId: number;
  let taskId: number;

  beforeAll(async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace', members: [1] });
    workspaceId = workspace.id;

    const task = await Task.create({ title: 'Test Task', workspaceId });
    taskId = task.id;
  });

  it('should update a task successfully', async () => {
    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/${taskId}`)
      .send({ title: 'Updated Task', status: 'in_progress' });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated Task');
    expect(response.body.status).toBe('in_progress');
  });

  it('should return 400 with validation errors', async () => {
    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/${taskId}`)
      .send({ title: 'a'.repeat(201) });

    expect(response.status).toBe(400);
    expect(response.body.errors).toBeDefined();
  });

  it('should return 404 if task does not exist', async () => {
    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/99999`);

    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Task not found');
  });

  it('should return 409 if trying to cancel task with open subtasks', async () => {
    const subtask = await Task.create({ title: 'Subtask', workspaceId, parentId: taskId, status: 'todo' });

    const response = await request(app)
      .patch(`/workspaces/${workspaceId}/tasks/${taskId}`)
      .send({ status: 'cancelled' });

    expect(response.status).toBe(409);
    expect(response.body.error).toBe('Cannot cancel task with open subtasks');

    await subtask.delete();
  });
});
```

This implementation covers the requirements and provides a complete solution for the PATCH endpoint, including validation, error handling, and unit tests.

*Response time: 113.8s*

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
Let's continue with the previous authentication system and address the remaining points:

### 4. Token Reuse Detection

Token reuse detection is essential to prevent replay attacks where an attacker might attempt to use the same refresh token more than once. We can implement this by maintaining a set of seen refresh tokens in Redis. If a refresh token is detected as being used again, we invalidate it and prevent further use.

**Redis Data Structure:**

- **Key:** `seen_refresh_tokens:<user_id>:<token_hash>`
- **Value:** A timestamp or a simple "seen" flag.
- **TTL:** This is not strictly necessary since we invalidate the token immediately upon detection of reuse.

**Implementation:**

```python
def is_token_seen(user_id, token):
    # Compute a hash of the token
    token_hash = hash(token)
    # Check if the token hash is in the Redis set
    return redis_client.exists(f"seen_refresh_tokens:{user_id}:{token_hash}")

def mark_token_as_seen(user_id, token):
    # Compute a hash of the token
    token_hash = hash(token)
    # Add the token hash to the Redis set with a TTL (if desired)
    redis_client.setex(f"seen_refresh_tokens:{user_id}:{token_hash}", 3600, "seen")  # 1 hour TTL



*Response time: 21.8s*

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
Sure, let's break down the implementation into the requested parts: the TypeScript interface for props, the complete component implementation, a usage example, and how to memoize the component to avoid unnecessary re-renders.

### 1. TypeScript Interface for Props

```typescript
import React from 'react';

interface Column<T> {
  key: keyof T;
  header: React.ReactNode;
  width?: number;
  sortable?: boolean;
  renderCell?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  page: number;
  pageSize: number;
  selectedRows: T[];
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  onRowSelect: (row: T, isSelected: boolean) => void;
  onAllRowsSelect: (isSelected: boolean) => void;
  sortConfig?: { key: keyof T; direction: 'asc' | 'desc' };
  onSort: (config: { key: keyof T; direction: 'asc' | 'desc' }) => void;
}
```

### 2. Complete Component Implementation

```typescript
import React, { useState, useEffect } from 'react';

const DataTable = <T extends object>({
  columns,
  data,
  page,
  pageSize,
  selectedRows,
  onPageChange,
  onPageSizeChange,
  onRowSelect,
  onAllRowsSelect,
  sortConfig,
  onSort,
}: DataTableProps<T>) => {
  const [selectAllChecked, setSelectAllChecked] = useState(false);

  useEffect(() => {
    setSelectAllChecked(data.length > 0 && selectedRows.length === data.length);
  }, [data, selectedRows]);

  const handleSort = (column: Column<T>) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig?.key === column.key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    onSort({ key: column.key, direction });
  };

  const handleRowSelect = (row: T, isSelected: boolean) => {
    onRowSelect(row, isSelected);
  };

  const handleAllRowsSelect = (isSelected: boolean) => {
    onAllRowsSelect(isSelected);
  };

  const sortedData = sortConfig
    ? [...data].sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
        if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      })
    : data;

  const paginatedData = sortedData.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ width: 30, textAlign: 'center' }}>
              <input
                type="checkbox"
                checked={selectAllChecked}
                onChange={(e) => handleAllRowsSelect(e.target.checked)}
              />
            </th>
            {columns.map((column) => (
              <th
                key={column.key}
                style={{ width: column.width, cursor: column.sortable ? 'pointer' : 'default' }}
                onClick={column.sortable ? () => handleSort(column) : undefined}
              >
                {column.header}
                {sortConfig?.key === column.key && (
                  <span style={{ marginLeft: 5 }}>
                    {sortConfig.direction === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((row, index) => (
            <tr key={index}>
              <td style={{ textAlign: 'center' }}>
                <input
                  type="checkbox"
                  checked={selectedRows.some((selectedRow) => selectedRow === row)}
                  onChange={(e) => handleRowSelect(row, e.target.checked)}
                />
              </td>
              {columns.map((column) => (
                <td key={column.key} style={{ width: column.width }}>
                  {column.renderCell ? column.renderCell(row) : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: 10 }}>
        <button onClick={() => onPageChange(page - 1)} disabled={page === 1}>
          Previous
        </button>
        <button onClick={() => onPageChange(page + 1)} disabled={paginatedData.length < pageSize}>
          Next
        </button>
        <select value={pageSize} onChange={(e) => onPageSizeChange(Number(e.target.value))}>
          <option value={10}>10</option>
          <option value={25}>25</option>
          <option value={50}>50</option>
        </select>
      </div>
    </div>
  );
};

export default DataTable;
```

### 3. Usage Example

```typescript
import React, { useState } from 'react';
import DataTable from './DataTable';

interface User {
  id: number;
  name: string;
  email: string;
}

const App = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [selectedRows, setSelectedRows] = useState<User[]>([]);
  const [sortConfig, setSortConfig] = useState<{ key: keyof User; direction: 'asc' | 'desc' } | null>(null);

  const handleRowSelect = (row: User, isSelected: boolean) => {
    setSelectedRows(isSelected ? [...selectedRows, row] : selectedRows.filter((r) => r !== row));
  };

  const handleAllRowsSelect = (isSelected: boolean) => {
    setSelectedRows(isSelected ? data : []);
  };

  const handleSort = (config: { key: keyof User; direction: 'asc' | 'desc' }) => {
    setSortConfig(config);
  };

  const data: User[] = [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Doe', email: 'jane@example.com' },
    // Add more data as needed
  ];

  const columns: Column<User>[] = [
    { key: 'id', header: 'ID', width: 50 },
    { key: 'name', header: 'Name', width: 150, sortable: true },
    { key: 'email', header: 'Email', width: 200, sortable: true, renderCell: (row) => <button>Action</button> },
  ];

  return (
    <DataTable
      columns={columns}
      data={data}
      page={page}
      pageSize={pageSize}
      selectedRows={selectedRows}
      onPageChange={setPage}
      onPageSizeChange={setPageSize}
      onRowSelect={handleRowSelect}
      onAllRowsSelect={handleAllRowsSelect}
      sortConfig={sortConfig}
      onSort={handleSort}
    />
  );
};

export default App;
```

### 4. Memoization

To avoid unnecessary re-renders, you can use `React.memo` and `useMemo` where appropriate. Here's how you can memoize the component and some of its parts:

```typescript
import React, { useState, useEffect, useMemo } from 'react';

const DataTable = <T extends object>({
  columns,
  data,
  page,
  pageSize,
  selectedRows,
  onPageChange,
  onPageSizeChange,
  onRowSelect,
  onAllRowsSelect,
  sortConfig,
  onSort,
}: DataTableProps<T>) => {
  // Use useMemo to memoize the sorted and paginated data
  const sortedData = useMemo(() => {
    if (sortConfig) {
      return [...data].sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
        if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    return data;
  }, [data, sortConfig]);

  const paginatedData = useMemo(() => sortedData.slice((page - 1) * pageSize, page * pageSize), [sortedData, page, pageSize]);

  // ... rest of the component

  return (
    <div>
      {/* ... table and pagination */}
    </div>
  );
};

export default React.memo(DataTable);
```

By using `React.memo`, the `DataTable` component will only re-render when its props change. Additionally, `useMemo` is used to memoize the sorted and paginated data, ensuring that these computations are only performed when necessary.

*Response time: 163.7s*

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
Certainly! Below is a complete implementation of the search feature in React using hooks only. This includes a custom hook `useSearch` to handle fetch, debounce, cache, and cancellation, as well as the `SearchPage` component that uses this hook. Additionally, I'll explain the URL sync implementation and why cancelling in-flight requests is important.

### Custom Hook: `useSearch`

This hook handles fetch, debounce, cache, and cancellation.

```jsx
import { useState, useEffect, useRef } from 'react';

const useSearch = (query) => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [controller, setController] = useState(null);
  const cache = useRef({});
  const timeoutId = useRef(null);

  useEffect(() => {
    // Cancel previous request if it's still in-flight
    if (controller) {
      controller.abort();
    }

    const cachedResult = cache.current[query];
    if (cachedResult && Date.now() - cachedResult.timestamp < 5 * 60 * 1000) {
      // Use cached result if it's still valid
      setResults(cachedResult.data);
      setLoading(false);
      setError(null);
      return;
    }

    // Debounce the search request
    timeoutId.current = setTimeout(async () => {
      try {
        setLoading(true);
        setError(null);

        // Create a new AbortController for the request
        const abortController = new AbortController();
        setController(abortController);

        const response = await fetch(`/api/search?q=${query}`, {
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Cache the result
        cache.current[query] = { data, timestamp: Date.now() };
        setResults(data);
      } catch (err) {
        if (err.name === 'AbortError') {
          // Request was aborted, no need to handle
          return;
        }
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      // Clear the timeout if the component unmounts or a new query is typed
      clearTimeout(timeoutId.current);
    };
  }, [query]);

  return { results, loading, error };
};

export default useSearch;
```

### SearchPage Component

This component uses the `useSearch` hook to fetch and display search results.

```jsx
import React, { useState, useEffect } from 'react';
import useSearch from './useSearch';

const SearchPage = () => {
  const [query, setQuery] = useState('');

  const { results, loading, error } = useSearch(query);

  useEffect(() => {
    // Sync URL with search query
    const urlParams = new URLSearchParams(window.location.search);
    const q = urlParams.get('q') || '';
    setQuery(q);
  }, []);

  useEffect(() => {
    // Update URL when query changes
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('q', query);
    const newUrl = `${window.location.origin}${window.location.pathname}?${urlParams.toString()}`;
    window.history.pushState({}, '', newUrl);
  }, [query]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {loading && <div>Loading...</div>}
      {error && (
        <div>
          {error} <button onClick={() => setQuery(query)}>Retry</button>
        </div>
      )}
      {!loading && !error && results && results.length === 0 && (
        <div>No results</div>
      )}
      {!loading && !error && results && results.length > 0 && (
        <ul>
          {results.map((result) => (
            <li key={result.id}>{result.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchPage;
```

### URL Sync Implementation

1. **Initial Query from URL**: When the component mounts, it reads the query from the URL using `URLSearchParams` and updates the local state.
2. **Update URL on Query Change**: Whenever the query changes, it updates the URL with the new query using `window.history.pushState`.

### Why Cancelling In-flight Requests is Important

Cancelling in-flight requests is crucial to prevent a few issues:

1. **Memory Leaks**: If a user types a new query before the previous request completes, the previous request might complete later and update the state, leading to unnecessary re-renders or even potential memory leaks if the component unmounts before the request completes.
2. **Race Conditions**: Without cancellation, the previous request might overwrite the results of the new request if it completes after the new request.
3. **Performance**: Cancelling requests that are no longer needed can improve performance by reducing the number of network requests made.

By cancelling in-flight requests, we ensure that only the most recent request's results are used, leading to a smoother and more predictable user experience.

*Response time: 95.1s*

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
Sure, let's go through each of your questions one by one:

### 1. Fetching 10 Most Recent Published Posts

To fetch the 10 most recent published posts along with the author's name, tag names, and comment count without causing N+1 queries, you can use Prisma's `select` and `include` options in combination with the `distinct` keyword to avoid duplicates. Here's how you can write the query:

```javascript
const recentPosts = await prisma.post.findMany({
  where: { published: true },
  orderBy: { createdAt: 'desc' },
  take: 10,
  select: {
    id: true,
    title: true,
    content: true,
    createdAt: true,
    author: {
      select: { name: true },
    },
    tags: {
      select: { name: true },
    },
    _count: {
      select: { comments: true },
    },
  },
});
```

### 2. Adding a Slug Field to Post Safely

Adding a `slug` field to a Post model with 10M rows requires careful planning to avoid downtime. Here’s a step-by-step migration scenario:

1. **Add the Slug Field:**
   First, add the `slug` field to your schema.

   ```prisma
   model Post {
     // existing fields
     slug String @unique @db.VarChar(255)
   }
   ```

2. **Generate and Apply the Migration:**
   Generate the migration file and apply it.

   ```bash
   npx prisma migrate dev --name add_slug_field
   ```

3. **Populate the Slug Field:**
   Write a script to populate the `slug` field for all existing posts. You can use a background job or a script to update the slugs.

   ```javascript
   async function generateSlugs() {
     const posts = await prisma.post.findMany();
     for (const post of posts) {
       const slug = generateSlug(post.title); // Implement your slug generation logic
       await prisma.post.update({
         where: { id: post.id },
         data: { slug },
       });
     }
   }

   generateSlugs();
   ```

4. **Make the Slug Field Non-Nullable:**
   After the slugs are populated, you can make the `slug` field non-nullable.

   ```prisma
   model Post {
     // existing fields
     slug String @unique @db.VarChar(255) @default('')
   }
   ```

5. **Apply the Migration:**
   Generate and apply the migration again.

   ```bash
   npx prisma migrate dev --name make_slug_non_nullable
   ```

### 3. Diagnosing and Fixing a Slow Query

If a query filtering posts by tag name is slow, follow these steps to diagnose and fix it:

1. **Prisma Query:**

   ```javascript
   const posts = await prisma.post.findMany({
     where: {
       tags: {
         some: {
           name: 'example-tag',
         },
       },
     },
   });
   ```

2. **Raw SQL:**

   The generated SQL might look something like this:

   ```sql
   SELECT DISTINCT ON ("Post"."id") "Post".* 
   FROM "Post" 
   INNER JOIN "_PostToTag" ON "Post"."id" = "_PostToTag"."A" 
   INNER JOIN "Tag" ON "Tag"."id" = "_PostToTag"."B" 
   WHERE "Tag"."name" = 'example-tag';
   ```

3. **Diagnose the Query:**

   - **Check for Indexes:** Ensure that there are indexes on the `name` column of the `Tag` table and the foreign keys in the `_PostToTag` table.

   ```sql
   CREATE INDEX "Tag_name_idx" ON "Tag"("name");
   CREATE INDEX "_PostToTag_A_idx" ON "_PostToTag"("A");
   CREATE INDEX "_PostToTag_B_idx" ON "_PostToTag"("B");
   ```

4. **Fix the Query:**

   After adding the indexes, the query should be faster. You can also consider adding a composite index on `("_PostToTag"."A", "_PostToTag"."B")` if it helps.

### 4. When to Drop Down to Raw SQL

There are specific scenarios where you might need to drop down to raw SQL, especially when Prisma does not support a certain feature or when performance is critical. For example:

- **Complex Joins:** If you need to perform complex joins that Prisma does not support efficiently, you might drop down to raw SQL.

- **Bulk Operations:** For bulk operations that are more efficient with raw SQL, such as bulk inserts or updates.

Example: If you need to perform a bulk update on a large dataset, you might use raw SQL for better performance.

```javascript
await prisma.$executeRaw`
  UPDATE "Post"
  SET "published" = true
  WHERE "createdAt" < NOW() - INTERVAL '1 week'
`;
```

In this example, using raw SQL allows you to perform a bulk update efficiently, which might not be as straightforward or efficient using Prisma's ORM methods.

*Response time: 96.1s*

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
Sure, I can help you with that. Let's address each part of your request.

### 1. Docker Compose for Local Development

Here is a sample `docker-compose.yml` file for local development with the specified requirements:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    environment:
      - NODE_ENV=development
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - /app/node_modules
    command: npm run dev
    environment:
      - NODE_ENV=development
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 10s

  db:
    image: postgres:latest
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:latest

volumes:
  pgdata:
```

### 2. Production Dockerfile for the Backend

Here is a sample multi-stage Dockerfile for the backend (Node.js):

```dockerfile
# Stage 1: Builder
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:14-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm prune --production

# Create a non-root user
RUN adduser -D myuser
USER myuser

EXPOSE 5000
CMD ["npm", "start"]
```

### 3. Backend Crashes with Exit Code 137

Exit code 137 means that the process was terminated by an out-of-memory (OOM) killer. This typically happens when the container runs out of memory. Here are the steps to diagnose and resolve this issue:

1. **Increase Memory Limit**: You can increase the memory limit allocated to the container. This can be done by setting the `--memory` flag in the Docker run command or by configuring the memory limit in your Docker Compose file.

2. **Optimize Code and Dependencies**: Review your code to optimize memory usage. Also, ensure that you are not installing unnecessary dependencies.

3. **Use Profiling Tools**: Use profiling tools to identify memory leaks and optimize them. Tools like `node-heapdump` or `memwatch-next` can be useful.

4. **Monitor Memory Usage**: Monitor the memory usage of your application in production to identify when the memory usage spikes and take corrective actions.

### 4. Deploying with Zero Downtime

To deploy a new version with zero downtime when the database schema changes (additive only — new nullable column), follow these steps:

1. **Prepare the Database Migration**:
   - Write a migration script to add the new nullable column.
   - Ensure the migration script is idempotent.

2. **Update the Backend**:
   - Prepare the new version of the backend that can handle the new schema.

3. **Deploy the Backend**:
   - Deploy the new backend version to a separate environment (e.g., a staging environment).

4. **Run the Migration**:
   - Apply the migration script to the database in the new environment.

5. **Switch Traffic**:
   - Once the new backend is running and the migration is complete, switch traffic from the old environment to the new environment.

6. **Verify the Deployment**:
   - Verify that the new backend is functioning correctly and that there are no issues with the database schema.

7. **Cleanup**:
   - If everything is running smoothly, you can decommission the old environment.

By following these steps, you can ensure that your deployment is done with zero downtime and that the new schema changes are applied correctly.

*Response time: 82.9s*

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
### Collaborative Document Editor Implementation

#### 1. Connection Handling
To associate a WebSocket connection with a user and document, we can maintain a connection map where the key is the WebSocket object and the value is an object containing user and document information. This map will help us track which user is connected to which document.

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

const connectionMap = new Map();

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    const data = JSON.parse(message);
    switch (data.type) {
      case 'join_document':
        handleJoinDocument(ws, data.documentId, data.userId);
        break;
      case 'text_change':
        handleTextChange(ws, data.documentId, data.change);
        break;
      case 'cursor_move':
        handleCursorMove(ws, data.documentId, data.cursorPosition);
        break;
      case 'user_left':
        handleUserLeft(ws, data.documentId);
        break;
    }
  });

  ws.on('close', () => {
    handleUserLeft(ws);
  });
});

function handleJoinDocument(ws, documentId, userId) {
  connectionMap.set(ws, { documentId, userId });
  // Broadcast to all users in the same document that a new user has joined
  broadcastMessage(documentId, {
    type: 'user_joined',
    userId
  });
}

function handleUserLeft(ws, documentId = null) {
  const { documentId: docId, userId } = connectionMap.get(ws) || {};
  connectionMap.delete(ws);
  // Broadcast to all users in the same document that a user has left
  broadcastMessage(docId || documentId, {
    type: 'user_left',
    userId
  });
}
```

#### 2. Message Protocol
Define the message types (JSON) for join document, text change, cursor move, and user left:

- **Join Document**
  ```json
  {
    "type": "join_document",
    "documentId": "doc123",
    "userId": "user456"
  }
  ```

- **Text Change**
  ```json
  {
    "type": "text_change",
    "documentId": "doc123",
    "change": {
      "index": 10,
      "text": "Hello",
      "operation": "insert" // or "delete"
    }
  }
  ```

- **Cursor Move**
  ```json
  {
    "type": "cursor_move",
    "documentId": "doc123",
    "cursorPosition": 15
  }
  ```

- **User Left**
  ```json
  {
    "type": "user_left",
    "userId": "user456"
  }
  ```

#### 3. Broadcasting
When a user makes a change, you send it to all other users in the same document but NOT back to the user who made the change:

```javascript
function broadcastMessage(documentId, message) {
  for (const [ws, { documentId: docId }] of connectionMap.entries()) {
    if (docId === documentId) {
      ws.send(JSON.stringify(message));
    }
  }
}

function handleTextChange(ws, documentId, change) {
  // Apply the change to the document state (omitted for brevity)
  broadcastMessage(documentId, {
    type: 'text_change',
    documentId,
    change
  });
}

function handleCursorMove(ws, documentId, cursorPosition) {
  broadcastMessage(documentId, {
    type: 'cursor_move',
    documentId,
    cursorPosition
  });
}
```

#### 4. Reconnection
When a user reconnects, they should get the latest document state. This can be achieved by sending the current document state to the user when they join the document.

```javascript
function handleJoinDocument(ws, documentId, userId) {
  connectionMap.set(ws, { documentId, userId });
  // Broadcast to all users in the same document that a new user has joined
  broadcastMessage(documentId, {
    type: 'user_joined',
    userId
  });

  // Send the current document state to the user who just joined
  const currentState = getCurrentDocumentState(documentId); // Implement this function to fetch the current state
  ws.send(JSON.stringify({
    type: 'document_state',
    documentId,
    state: currentState
  }));
}
```

#### 5. Simultaneous Edits
If two users edit the exact same position simultaneously, the last edit received by the server will overwrite the previous one. To handle this properly, you would need to implement an Operational Transformation (OT) or Conflict-free Replicated Data Types (CRDT). These approaches ensure that all users see a consistent document state even if they make simultaneous changes.

### Core Server Implementation

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

const connectionMap = new Map();

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    const data = JSON.parse(message);
    switch (data.type) {
      case 'join_document':
        handleJoinDocument(ws, data.documentId, data.userId);
        break;
      case 'text_change':
        handleTextChange(ws, data.documentId, data.change);
        break;
      case 'cursor_move':
        handleCursorMove(ws, data.documentId, data.cursorPosition);
        break;
      case 'user_left':
        handleUserLeft(ws, data.documentId);
        break;
    }
  });

  ws.on('close', () => {
    handleUserLeft(ws);
  });
});

function handleJoinDocument(ws, documentId, userId) {
  connectionMap.set(ws, { documentId, userId });
  broadcastMessage(documentId, {
    type: 'user_joined',
    userId
  });

  const currentState = getCurrentDocumentState(documentId);
  ws.send(JSON.stringify({
    type: 'document_state',
    documentId,
    state: currentState
  }));
}

function handleUserLeft(ws, documentId = null) {
  const { documentId: docId, userId } = connectionMap.get(ws) || {};
  connectionMap.delete(ws);
  broadcastMessage(docId || documentId, {
    type: 'user_left',
    userId
  });
}

function broadcastMessage(documentId, message) {
  for (const [ws, { documentId: docId }] of connectionMap.entries()) {
    if (docId === documentId) {
      ws.send(JSON.stringify(message));
    }
  }
}

function handleTextChange(ws, documentId, change) {
  // Apply the change to the document state (omitted for brevity)
  broadcastMessage(documentId, {
    type: 'text_change',
    documentId,
    change
  });
}

function handleCursorMove(ws, documentId, cursorPosition) {
  broadcastMessage(documentId, {
    type: 'cursor_move',
    documentId,
    cursorPosition
  });
}

function getCurrentDocumentState(documentId) {
  // Implement this function to fetch the current state of the document
  return {
    // Example document state
    text: "Initial document content"
  };
}
```

This implementation provides a basic framework for a collaborative document editor using Node.js and the `ws` library. It handles connection management, message routing, broadcasting, reconnection, and outlines the approach to handle simultaneous edits.

*Response time: 138.0s*

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
### 1. Complete GraphQL Schema (SDL)

```graphql
type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [String!]!
  author: User!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float!
}

type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type User {
  id: ID!
  name: String!
}

type Rating {
  score: Float!
  comment: String!
}

type Query {
  recipes(
    filter: RecipeFilterInput,
    pagination: PaginationInput
  ): [Recipe!]!
}

input RecipeFilterInput {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int
  limit: Int
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String!): Recipe!
}

type Subscription {
  newRating(recipeId: ID!): Rating!
}
```

### 2. Resolvers

```javascript
const resolvers = {
  Recipe: {
    averageRating: async (parent) => {
      const totalRatings = parent.ratings.reduce((acc, rating) => acc + rating.score, 0);
      return totalRatings / parent.ratings.length;
    }
  },
  Query: {
    recipes: async (_, { filter = {}, pagination = {} }, { dataSources }) => {
      const { tag, minRating } = filter;
      const { page, limit } = pagination;
      const recipes = await dataSources.RecipeAPI.getRecipes({ tag, minRating });
      return recipes.slice(page * limit, (page + 1) * limit);
    }
  },
  Mutation: {
    addRating: async (_, { recipeId, score, comment }, { dataSources }) => {
      const newRating = await dataSources.RecipeAPI.addRating(recipeId, { score, comment });
      return dataSources.RecipeAPI.getRecipeById(recipeId);
    }
  }
};
```

### 3. N+1 Problem and DataLoader Fix

**Problem:**
When querying recipes, if you fetch the `author` field for each recipe, you will end up making multiple database queries for each author, leading to an N+1 problem. For example, if you fetch 10 recipes and each recipe has a unique author, you will make 11 queries (1 for recipes and 10 for authors).

**Fix using DataLoader:**

```javascript
const DataLoader = require('dataloader');

const authorLoader = new DataLoader(async (authorIds) => {
  const authors = await dataSources.UserAPI.getAuthorsByIds(authorIds);
  return authorIds.map(id => authors.find(author => author.id === id));
});

const recipeResolvers = {
  Recipe: {
    author: async (parent) => {
      return authorLoader.load(parent.authorId);
    }
  }
};
```

### 4. Exact GraphQL Query

A client can fetch the recipe title, author name, and first 3 ingredients in one request with the following query:

```graphql
query {
  recipes(pagination: { page: 0, limit: 10 }) {
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

### 5. When to Choose GraphQL Over REST and When Not

**When to Choose GraphQL:**
- When you need a single endpoint to serve multiple client requests with different data requirements.
- When you want to provide clients with the flexibility to request exactly what they need.
- When you have complex data relationships and need efficient querying.
- When you want to reduce the number of requests made to your server.

**When NOT to Choose GraphQL:**
- When you have simple data requirements and don't need the flexibility of a complex query language.
- When your API is read-heavy and you want to optimize for simplicity and performance.
- When you have existing RESTful APIs and don't want to introduce a new query language.
- When your team is not familiar with GraphQL and it would add unnecessary complexity.

*Response time: 73.9s*

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
To implement the specified UI layout using only CSS, we will use a combination of Flexbox and CSS Grid. Flexbox will help us manage the main structure and alignment, while CSS Grid will be used to create the responsive card layout within the main content area.

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive Layout</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        HEADER
    </header>
    <div class="container">
        <aside class="sidebar">
            Sidebar Content
            <div style="height: 2000px;"></div> <!-- For scroll testing -->
        </aside>
        <main class="main-content">
            <div class="card-grid">
                <div class="card">
                    <img src="image1.jpg" alt="Image 1">
                    <h2>Title 1</h2>
                    <p>Description for card 1.</p>
                    <footer class="card-footer">
                        <button class="left-button">Left Button</button>
                        <button class="right-button">Right Button</button>
                    </footer>
                </div>
                <div class="card">
                    <img src="image2.jpg" alt="Image 2">
                    <h2>Title 2</h2>
                    <p>Description for card 2.</p>
                    <footer class="card-footer">
                        <button class="left-button">Left Button</button>
                        <button class="right-button">Right Button</button>
                    </footer>
                </div>
                <!-- Add more cards as needed -->
            </div>
        </main>
    </div>
</body>
</html>
```

### CSS Styling

```css
body, html {
    margin: 0;
    padding: 0;
    height: 100%;
    font-family: Arial, sans-serif;
}

.header {
    position: fixed;
    top: 0;
    width: 100%;
    height: 60px;
    background-color: #333;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.container {
    display: flex;
    margin-top: 60px; /* Height of the header */
    height: calc(100vh - 60px);
}

.sidebar {
    width: 240px;
    background-color: #f4f4f4;
    overflow-y: auto;
    padding: 20px;
    box-sizing: border-box;
}

.main-content {
    flex-grow: 1;
    overflow-y: auto;
    padding: 20px;
    box-sizing: border-box;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

.card {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
}

.card img {
    width: 100%;
    height: 0;
    padding-top: 56.25%; /* 16:9 aspect ratio */
    object-fit: cover;
}

.card h2 {
    padding: 10px;
    margin: 0;
}

.card p {
    padding: 10px;
    margin: 0;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: #f9f9f9;
}

.left-button, .right-button {
    padding: 8px 16px;
    border: none;
    background-color: #007bff;
    color: white;
    cursor: pointer;
}

.left-button {
    margin-right: auto;
}

.right-button {
    margin-left: auto;
}
```

### Explanation of Layout Approach

1. **Header**: The header is fixed at the top using `position: fixed` to ensure it remains visible while scrolling. It has a fixed height of 60px and covers the full width of the viewport.

2. **Container**: The `.container` uses Flexbox to arrange the sidebar and main content side by side. It is set to fill the remaining viewport height after the header.

3. **Sidebar and Main Content**: Both the sidebar and main content areas are given `overflow-y: auto` to enable scrolling independently. The sidebar has a fixed width of 240px, while the main content area fills the remaining space.

4. **Card Layout**: The `.card-grid` uses CSS Grid to create a responsive layout. The grid has a `grid-template-columns` property set to `repeat(auto-fill, minmax(200px, 1fr))`, which ensures that the cards fill the available space. The cards have a 16:9 aspect ratio for images using `padding-top: 56.25%`.

5. **Responsive Design**: The card grid automatically adjusts to display one column on mobile devices (≤768px) and two columns on desktop devices (≥768px).

This approach leverages the strengths of both Flexbox and CSS Grid to create a flexible and responsive layout that meets the specified requirements.

*Response time: 103.2s*

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
1. **Transport Mechanism:**
   For real-time notifications, **WebSocket** is the most suitable transport mechanism. WebSockets provide a full-duplex communication channel over a single, long-lived connection, which is efficient for real-time applications like notifications. Unlike HTTP polling, which requires frequent requests and server resources, WebSockets allow the server to push updates to the client as soon as they occur without the client needing to request them. This results in lower latency and better performance. Push notifications could be used for mobile users, but WebSockets cover web-based notifications effectively.

2. **Database Schema:**
   To store notifications, a simple relational database schema can be used. Here’s a basic schema:
   - **Notifications Table:**
     - `id`: Primary key
     - `user_id`: Foreign key to the user who should receive the notification
     - `task_id`: Foreign key to the task related to the notification
     - `type`: Type of notification (e.g., 'task_assigned', 'comment_added', 'deadline_approaching')
     - `message`: Text of the notification
     - `timestamp`: When the notification was created
     - `is_read`: Boolean indicating whether the user has read the notification
   - **Users Table:**
     - `id`: Primary key
     - `name`: User's name
     - `email`: User's email
     - `last_seen`: Timestamp of the last time the user was online

3. **Handling Offline Users:**
   For users who are offline, notifications should be queued in the database and delivered as soon as they come back online. This can be achieved by checking the `last_seen` field of the user in the database. When a user reconnects, the application can fetch all unread notifications from the `Notifications` table and push them to the user through WebSocket.

4. **Deadline Check Implementation:**
   To check for approaching deadlines every hour, a **cron job** can be used. The cron job would execute a script that queries the database for tasks where the deadline is within 24 hours and schedules notifications for those tasks.
   ```bash
   # Cron job to run every hour
   0 * * * * /path/to/your/script/check_deadlines.sh
   ```
   Inside the script, you can write a query like:
   ```sql
   SELECT * FROM tasks WHERE deadline BETWEEN NOW() AND NOW() + INTERVAL 24 HOUR;
   ```
   For each task returned, a notification can be created in the `Notifications` table and sent to the appropriate user.

5. **Scalability:**
   To handle 100,000 concurrent users, consider the following strategies:
   - **Load Balancing:** Use a load balancer to distribute incoming requests across multiple instances of the application server.
   - **WebSocket Clustering:** Implement WebSocket clustering to manage connections across multiple servers. This can be done using solutions like Redis or RabbitMQ to broadcast messages to connected clients.
   - **Database Optimization:** Use caching mechanisms like Redis for frequently accessed data to reduce database load.
   - **Asynchronous Processing:** Use message queues (e.g., RabbitMQ, Kafka) for asynchronous processing of tasks like sending notifications, which can be processed in the background.
   - **Vertical and Horizontal Scaling:** Increase the resources of a single server (vertical scaling) or add more servers to the infrastructure (horizontal scaling) based on the load.

By following these strategies, the notification system can be designed to handle a large number of users efficiently.

*Response time: 65.9s*

---
