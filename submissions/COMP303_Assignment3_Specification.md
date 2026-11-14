# COMP303: Enterprise Application Development — Assignment 3
## Project Specification & Architecture Document
**Student Name:** Ean Bynoe  
**Student ID:** `301390261`  
**Course & Section:** COMP303 (SEC. 001)  
**Instructor:** Dr. Vinay Vaithilingam  
**Project Name:** `EanBynoe_COMP303_Assignment3`  
**Main Class:** `EanBynoe_COMP303_Assign3App.java`  
**Port:** `http://localhost:8080`  
**Database:** MongoDB (`mongodb://localhost:27017/online_marketplace_db`)  

---

## 1. System Overview
An asynchronous, reactive Online Marketplace Management System built with **Spring Boot 3.x**, **Spring Data Reactive MongoDB**, and **Thymeleaf**. The platform manages:
- **Sellers**: Vendor profiles, contact information, business classification, and rating metrics.
- **Products**: Catalog items categorized under Electronics, Clothing, Books, and Home & Kitchen with real-time stock quantity and availability flags.
- **Customer Orders**: Order processing lifecycle (`Pending` -> `Confirmed` -> `Shipped` -> `Delivered`) featuring automated stock inventory decrement and validation.

---

## 2. Package Architecture
```text
src/main/java/com/centennial/comp303/assignment3/
├── EanBynoe_COMP303_Assign3App.java
├── model/
│   ├── Seller.java
│   ├── Product.java
│   └── CustomerOrder.java
├── repository/
│   ├── ReactiveSellerRepository.java
│   ├── ReactiveProductRepository.java
│   └── ReactiveCustomerOrderRepository.java
├── service/
│   ├── SellerService.java
│   ├── ProductService.java
│   └── CustomerOrderService.java
├── controller/
│   ├── api/
│   │   ├── SellerRestController.java
│   │   ├── ProductRestController.java
│   │   └── CustomerOrderRestController.java
│   └── web/
│       └── MarketplaceWebController.java
└── exception/
    ├── ResourceNotFoundException.java
    └── InsufficientStockException.java
```

---

## 3. Entity Schemas (MongoDB Document Mappings)

### 3.1 Seller (`sellers` collection)
```java
@Document(collection = "sellers")
public class Seller {
    @Id
    private String id;
    private Long sellerId; // Unique business key
    private String sellerName;
    private String email;
    private String businessType; // "Individual", "Small Business", "Corporation"
    private String city;
    private Double rating; // 1.0 - 5.0
}
```

### 3.2 Product (`products` collection)
```java
@Document(collection = "products")
public class Product {
    @Id
    private String id;
    private Long productId; // Unique business key
    private String productName;
    private String category; // "Electronics", "Clothing", "Books", "Home & Kitchen"
    private Double price;
    private Integer stockQuantity;
    private Boolean availability;
    private Long sellerId; // Foreign key referencing Seller
}
```

### 3.3 CustomerOrder (`customer_orders` collection)
```java
@Document(collection = "customer_orders")
public class CustomerOrder {
    @Id
    private String id;
    private Long orderId; // Unique business key
    private String customerName;
    private String customerEmail;
    private Long productId;
    private Integer quantity;
    private String orderStatus; // "Pending", "Confirmed", "Shipped", "Delivered"
    private LocalDateTime orderTime;
    private Double totalAmount;
}
```

---

## 4. Reactive REST API Endpoints Specification

| Method | Endpoint | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/sellers` | — | Retrieve all registered sellers (`Flux<Seller>`) |
| `GET` | `/api/sellers/{sellerId}` | — | Retrieve seller by ID (`Mono<Seller>`) |
| `POST` | `/api/sellers` | `Seller` JSON | Register new seller with validation |
| `PUT` | `/api/sellers/{sellerId}` | `Seller` JSON | Update existing seller profile |
| `DELETE` | `/api/sellers/{sellerId}` | — | Remove seller |
| `GET` | `/api/products` | — | Retrieve all catalog products |
| `GET` | `/api/products/category/{category}` | — | Query products by category |
| `POST` | `/api/products` | `Product` JSON | Create product (validates seller exists) |
| `GET` | `/api/orders` | — | Retrieve all customer orders |
| `POST` | `/api/orders` | `CustomerOrder` JSON | Create order (checks & decrements stock) |
| `PUT` | `/api/orders/{id}/cancel` | — | Cancel order & restore inventory (Innovation) |

---

## 5. Innovation Feature Implementation (5/5 Marks)
**Inventory Rollback & Dynamic Stock Synchronization:**
1. When a `CustomerOrder` is placed:
   - Validates that `stockQuantity >= order.getQuantity()`.
   - Decrements stock atomically. If stock drops to `0`, automatically flips `availability = false`.
2. When a `CustomerOrder` is canceled (`PUT /api/orders/{id}/cancel`):
   - Restores the product inventory quantity.
   - Automatically re-activates `availability = true`.
