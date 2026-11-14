package com.centennial.comp303.assignment3.service;

import com.centennial.comp303.assignment3.exception.ResourceNotFoundException;
import com.centennial.comp303.assignment3.model.Product;
import com.centennial.comp303.assignment3.repository.ReactiveProductRepository;
import com.centennial.comp303.assignment3.repository.ReactiveSellerRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
public class ProductService {

    private final ReactiveProductRepository productRepository;
    private final ReactiveSellerRepository sellerRepository;

    public ProductService(ReactiveProductRepository productRepository, ReactiveSellerRepository sellerRepository) {
        this.productRepository = productRepository;
        this.sellerRepository = sellerRepository;
    }

    public Flux<Product> getAllProducts() {
        return productRepository.findAll();
    }

    public Mono<Product> getProductById(Long productId) {
        return productRepository.findByProductId(productId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Product not found with ID: " + productId)));
    }

    public Flux<Product> getProductsByCategory(String category) {
        return productRepository.findByCategoryIgnoreCase(category);
    }

    public Flux<Product> getProductsBySellerId(Long sellerId) {
        return productRepository.findBySellerId(sellerId);
    }

    public Mono<Product> createProduct(Product product) {
        return sellerRepository.existsBySellerId(product.getSellerId())
                .flatMap(sellerExists -> {
                    if (Boolean.FALSE.equals(sellerExists)) {
                        return Mono.error(new ResourceNotFoundException("Cannot add product; Seller ID not found: " + product.getSellerId()));
                    }
                    return productRepository.existsByProductId(product.getProductId())
                            .flatMap(productExists -> {
                                if (Boolean.TRUE.equals(productExists)) {
                                    return Mono.error(new IllegalArgumentException("Product ID already exists: " + product.getProductId()));
                                }
                                if (product.getAvailability() == null) {
                                    product.setAvailability(product.getStockQuantity() != null && product.getStockQuantity() > 0);
                                }
                                return productRepository.save(product);
                            });
                });
    }

    public Mono<Product> updateProduct(Long productId, Product updated) {
        return productRepository.findByProductId(productId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Product not found with ID: " + productId)))
                .flatMap(existing -> sellerRepository.existsBySellerId(updated.getSellerId())
                        .flatMap(sellerExists -> {
                            if (Boolean.FALSE.equals(sellerExists)) {
                                return Mono.error(new ResourceNotFoundException("Seller ID not found: " + updated.getSellerId()));
                            }
                            existing.setProductName(updated.getProductName());
                            existing.setCategory(updated.getCategory());
                            existing.setPrice(updated.getPrice());
                            existing.setStockQuantity(updated.getStockQuantity());
                            existing.setAvailability(updated.getStockQuantity() > 0);
                            existing.setSellerId(updated.getSellerId());
                            return productRepository.save(existing);
                        }));
    }

    public Mono<Void> deleteProduct(Long productId) {
        return productRepository.findByProductId(productId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Product not found with ID: " + productId)))
                .flatMap(existing -> productRepository.deleteByProductId(productId));
    }
}
