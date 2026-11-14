package com.centennial.comp303.assignment3.repository;

import com.centennial.comp303.assignment3.model.CustomerOrder;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public interface ReactiveCustomerOrderRepository extends ReactiveMongoRepository<CustomerOrder, String> {
    Mono<CustomerOrder> findByOrderId(Long orderId);
    Flux<CustomerOrder> findByOrderStatusIgnoreCase(String orderStatus);
    Flux<CustomerOrder> findByProductId(Long productId);
    Mono<Void> deleteByOrderId(Long orderId);
}
