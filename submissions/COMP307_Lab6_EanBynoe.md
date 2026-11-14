# COMP307 — Software Security
## Lab Assignment 6: Web Application Security Vulnerabilities (DVWA)
**Student Name:** Ean Bynoe  
**Student ID:** `301390261`  
**Course & Section:** COMP307 (SEC. 002) — Software Security  
**Instructor:** Bindu Goel  
**Date:** November 15, 2026  
**File Name:** `Ean_Bynoe_COMP307_Lab6.docx` / `Ean_Bynoe_COMP307_Lab6.pdf`

---

## 1. Executive Summary & Lab Objectives
The objective of this hands-on laboratory exercise is to analyze, exploit, and remediate critical web application security vulnerabilities within the Damn Vulnerable Web Application (DVWA) testbed environment. Specifically, this report investigates:
1. **Reflected Cross-Site Scripting (XSS)** at **Low** and **Medium** security levels.
2. **SQL Injection (SQLi)** vulnerabilities allowing authentication bypass and database exfiltration.
3. **Source Code Auditing**: Comparative analysis between vulnerable PHP implementations (Low/Medium) and secure, hardened production code (High/Impossible).
4. **Remediation Engineering**: Establishing defensive programming standards including contextual HTML entity encoding (`htmlspecialchars`) and parameterized queries (Prepared Statements with PDO).

---

## 2. Environment & Testbed Setup
- **Target Application:** Damn Vulnerable Web Application (DVWA) v1.10
- **Server Platform:** Apache/2.4.52 (Ubuntu Linux / Metasploitable), PHP 8.1
- **Database Engine:** MariaDB / MySQL 10.6
- **Testing Browser / Client:** Firefox Developer Edition / Burp Suite Community v2026.1
- **Target URL:** `http://localhost/dvwa/vulnerabilities/`

---

## 3. Exercise 1: Reflected Cross-Site Scripting (XSS)

### 3.1 Step 1: Normal Execution & Reflection Verification
- **Target Module:** `vulnerabilities/xss_r/`
- **Initial Test Input:** `John`
- **Observation:** The application echoes:
  ```text
  Hello John
  ```
- **Vulnerability Mechanism:** The server receives the `name` parameter via `$_GET['name']` and concatenates it directly into the HTTP response body without sanitization or HTML entity encoding.

### 3.2 Step 2: Exploitation at Low Security Level
- **Security Level:** `Low`
- **Test Payload:**
  ```html
  <script>alert('XSS Reflected - Ean Bynoe 301390261')</script>
  ```
- **Execution Result:** The web browser parses the unescaped `<script>` tag as executable JavaScript rather than plain text. A modal alert dialog pops up with the message:
  ```text
  "XSS Reflected - Ean Bynoe 301390261"
  ```
- **Impact Analysis:** In a production application, an attacker can leverage reflected XSS to execute malicious scripts in the victim's session, hijack session cookies (`document.cookie`), redirect users to credential-harvesting phishing portals, or perform unauthorized client-side actions.

```
+-----------------------------------------------------------------------+
|  [Screenshot 1: Low Security Reflected XSS Alert Execution]           |
|  Caption: DVWA Reflected XSS Low Security displaying alert box with    |
|  student ID 301390261 and payload in URL parameter string.            |
+-----------------------------------------------------------------------+
```

### 3.3 Step 3: Exploitation at Medium Security Level (Filter Evasion)
- **Security Level:** `Medium`
- **Server Defensive Mechanism:** The server implements a blacklisting filter:
  ```php
  $name = str_replace('<script>', '', $_GET['name']);
  ```
- **Bypass Technique 1 (Case Sensitivity Evasion):**
  Because PHP's `str_replace()` is strictly case-sensitive, it matches only the exact lowercase string `<script>`. An attacker bypasses this by utilizing mixed-case or uppercase tags:
  ```html
  <SCRIPT>alert('Medium XSS Bypassed - Ean Bynoe')</SCRIPT>
  ```
- **Bypass Technique 2 (Nested Tag Evasion):**
  Because `str_replace()` performs only a single non-recursive pass, nesting the tag causes the inner `<script>` to be stripped, leaving the outer tag intact:
  ```html
  <scr<script>ipt>alert('Medium Nested Bypass')</script>
  ```
- **Execution Result:** The script executes successfully, demonstrating that blacklist-based input sanitization is inherently flawed.

```
+-----------------------------------------------------------------------+
|  [Screenshot 2: Medium Security Filter Bypass Execution]              |
|  Caption: Reflected XSS Medium Security executing mixed-case tag       |
|  <SCRIPT>alert(...) bypass.                                           |
+-----------------------------------------------------------------------+
```

---

## 4. Exercise 2: SQL Injection (SQLi)

### 4.1 Step 1: Normal Query Execution
- **Target Module:** `vulnerabilities/sqli/`
- **Standard Input:** User ID `1`
- **Normal Output:**
  ```text
  ID: 1
  First name: admin
  Surname: admin
  ```
- **Underlying Database Query:**
  ```sql
  SELECT first_name, last_name FROM users WHERE user_id = '1';
  ```

### 4.2 Step 2: Exploitation at Low Security Level (Tautology Attack)
- **Security Level:** `Low`
- **Vulnerability Mechanism:** User input is directly interpolated into the SQL command string without parameterized binding.
- **Exploitation Payload:**
  ```sql
  1' OR '1'='1
  ```
- **Crafted Query Executed on Database:**
  ```sql
  SELECT first_name, last_name FROM users WHERE user_id = '1' OR '1'='1';
  ```
- **Execution Result:** Since `'1'='1'` evaluates to `TRUE` for every row in the `users` table, the query dumps the entire user database table:
  1. `ID: 1 | First name: admin | Surname: admin`
  2. `ID: 2 | First name: Gordon | Surname: Brown`
  3. `ID: 3 | First name: Hack | Surname: ME`
  4. `ID: 4 | First name: Pablo | Surname: Picasso`
  5. `ID: 5 | First name: Bob | Surname: Smith`

```
+-----------------------------------------------------------------------+
|  [Screenshot 3: SQL Injection Tautology Dump]                          |
|  Caption: DVWA SQL Injection Low Security showing user database table  |
|  dump via 1' OR '1'='1 payload.                                        |
+-----------------------------------------------------------------------+
```

### 4.3 Step 3: Information Gathering via UNION Injection
- **Payload:**
  ```sql
  1' UNION SELECT user, password FROM users #
  ```
- **Execution Result:** The application extracts user credentials and MD5 password hashes directly onto the client interface, enabling offline password cracking.

---

## 5. Source Code Analysis & Secure Remediation

### 5.1 XSS Code Comparison
#### Vulnerable Code (Low/Medium Security):
```php
// VULNERABLE: Direct output concatenation
if( isset( $_GET[ 'Submit' ] ) ) {
    $name = $_GET[ 'name' ];
    echo '<pre>Hello ' . $name . '</pre>';
}
```

#### Secure Remediation (Impossible Security Level):
```php
// SECURE: Contextual HTML entity encoding
if( isset( $_GET[ 'Submit' ] ) ) {
    checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
    $name = htmlspecialchars( $_GET[ 'name' ], ENT_QUOTES | ENT_HTML5, 'UTF-8' );
    echo '<pre>Hello ' . $name . '</pre>';
}
```
* **Explanation:** `htmlspecialchars()` transforms dangerous characters (`<`, `>`, `&`, `"`, `'`) into benign HTML entities (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#039;`). The browser renders the characters visually without interpreting them as executable markup.

---

### 5.2 SQL Injection Code Comparison
#### Vulnerable Code (Low Security):
```php
// VULNERABLE: Dynamic SQL string concatenation
$id = $_GET[ 'id' ];
$query  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
$result = mysqli_query($GLOBALS["___mysqli_ston"], $query);
```

#### Secure Remediation (Prepared Statements with PDO):
```php
// SECURE: Parameterized Queries with PDO
if( isset( $_GET[ 'Submit' ] ) ) {
    checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
    $id = $_GET[ 'id' ];
    $stmt = $pdo->prepare( 'SELECT first_name, last_name FROM users WHERE user_id = :id LIMIT 1;' );
    $stmt->bindParam( ':id', $id, PDO::PARAM_INT );
    $stmt->execute();
    $result = $stmt->fetchAll();
}
```
* **Explanation:** Parameterized queries strictly decouple SQL command instructions from user data. Even if a user enters `' OR '1'='1`, the database engine treats the entire input strictly as a literal value, rendering injection impossible.

---

## 6. Conclusion
This laboratory demonstrated how unvalidated user input creates critical vulnerabilities. Organizations must enforce **defense-in-depth**:
1. Strictly adopt **Prepared Statements / Parameterized Queries** across all persistence layers (Spring Data JPA, PDO).
2. Apply **Context-Aware Output Encoding** using mature templating engines (`htmlspecialchars`, React, Thymeleaf).
3. Deploy modern defensive controls including **Content Security Policy (CSP)** and Web Application Firewalls (WAF).
