# Send Welcome Mail

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Issues & Bugs
- Development
- Tests
- Dependencies

---

## Features

- If there is a stage called `Incoming`, then move ticket there. Do this check directly after the check for the Stage `draft`.(#6073)

---

## Configuration

To add the default agreement for contracts
-> Settings -> General Settings -> Default Media Agreement

---

## Usage

1. Send contracts to contacts
2. After both party signed, automatically welcome email will be sent
---

## Dependencies

### Odoo modules dependencies

| Module | Why used?       | Side effects 
|--------|-----------------|--------------|
| Mail   | Mail            |
| crm    | Contact acccess |              |     

### Python library dependencies

The module doesn't require any external Python library

---

## Limitations, Issues & Bugs

The module doesn't require any Limitations, Issues & Bugs

---
