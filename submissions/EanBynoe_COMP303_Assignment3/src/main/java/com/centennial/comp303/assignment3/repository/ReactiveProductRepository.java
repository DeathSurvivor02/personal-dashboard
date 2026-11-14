package com.centennial.comp303.assignment3.repository;

import com.centennial.comp303.assignment3.model.Product;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public interface ReactiveProductRepository extends ReactiveMongoRepository<Product, String> {
    Mono<Product> findByProductId(Long productId);
    Mono<Boolean> existsByProductId(Long productId);
    Flux<Product> findByCategoryIgnoreCase(String category);
    Flux<Product> findBySellerId(Long sellerId);
    Mono<Void> deleteByProductId(Long productId);
}
