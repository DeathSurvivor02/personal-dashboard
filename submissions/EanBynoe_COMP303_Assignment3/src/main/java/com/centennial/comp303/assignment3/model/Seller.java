package com.centennial.comp303.assignment3.model;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "sellers")
public class Seller {

    @Id
    private String id;

    @NotNull(message = "Seller ID is required")
    @Indexed(unique = true)
    private Long sellerId;

    @NotBlank(message = "Seller name is required")
    private String sellerName;

    @NotBlank(message = "Email is required")
    @Email(message = "Valid email is required")
    private String email;

    @NotBlank(message = "Business type is required")
    private String businessType; // Individual, Small Business, Registered Company

    @NotBlank(message = "City is required")
    private String city;

    @NotNull(message = "Rating is required")
    @DecimalMin(value = "0.0", message = "Rating must be >= 0.0")
    @DecimalMax(value = "5.0", message = "Rating must be <= 5.0")
    private Double rating;

    public Seller() {}

    public Seller(Long sellerId, String sellerName, String email, String businessType, String city, Double rating) {
        this.sellerId = sellerId;
        this.sellerName = sellerName;
        this.email = email;
        this.businessType = businessType;
        this.city = city;
        this.rating = rating;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public Long getSellerId() { return sellerId; }
    public void setSellerId(Long sellerId) { this.sellerId = sellerId; }

    public String getSellerName() { return sellerName; }
    public void setSellerName(String sellerName) { this.sellerName = sellerName; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getBusinessType() { return businessType; }
    public void setBusinessType(String businessType) { this.businessType = businessType; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public Double getRating() { return rating; }
    public void setRating(Double rating) { this.rating = rating; }
}
