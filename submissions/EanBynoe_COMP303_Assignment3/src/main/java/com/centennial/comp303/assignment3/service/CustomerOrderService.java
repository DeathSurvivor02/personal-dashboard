package com.centennial.comp303.assignment3.service;

import com.centennial.comp303.assignment3.exception.InsufficientStockException;
import com.centennial.comp303.assignment3.exception.ResourceNotFoundException;
import com.centennial.comp303.assignment3.model.CustomerOrder;
import com.centennial.comp303.assignment3.repository.ReactiveCustomerOrderRepository;
import com.centennial.comp303.assignment3.repository.ReactiveProductRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;

@Service
public class CustomerOrderService {

    private final ReactiveCustomerOrderRepository orderRepository;
    private final ReactiveProductRepository productRepository;

    public CustomerOrderService(ReactiveCustomerOrderRepository orderRepository, ReactiveProductRepository productRepository) {
        this.orderRepository = orderRepository;
        this.productRepository = productRepository;
    }

    public Flux<CustomerOrder> getAllOrders() {
        return orderRepository.findAll();
    }

    public Mono<CustomerOrder> getOrderById(Long orderId) {
        return orderRepository.findByOrderId(orderId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Order not found with ID: " + orderId)));
    }

    public Flux<CustomerOrder> getOrdersByStatus(String status) {
        return orderRepository.findByOrderStatusIgnoreCase(status);
    }

    /**
     * Places a new order, verifying product existence and sufficient stock,
     * and atomically decrementing the product inventory.
     */
    public Mono<CustomerOrder> createOrder(CustomerOrder order) {
        return productRepository.findByProductId(order.getProductId())
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Product not found with ID: " + order.getProductId())))
                .flatMap(product -> {
                    if (Boolean.FALSE.equals(product.getAvailability()) || product.getStockQuantity() < order.getQuantity()) {
                        return Mono.error(new InsufficientStockException(
                                "Insufficient stock for product '" + product.getProductName() + "'. Available: " + product.getStockQuantity()
                        ));
                    }

                    int newStock = product.getStockQuantity() - order.getQuantity();
                    product.setStockQuantity(newStock);
                    product.setAvailability(newStock > 0);

                    if (order.getOrderStatus() == null || order.getOrderStatus().isBlank()) {
                        order.setOrderStatus("Confirmed");
                    }
                    if (order.getOrderTime() == null) {
                        order.setOrderTime(LocalDateTime.now());
                    }
                    order.setTotalAmount(product.getPrice() * order.getQuantity());

                    return productRepository.save(product)
                            .then(orderRepository.save(order));
                });
    }

    public Mono<CustomerOrder> updateOrderStatus(Long orderId, String newStatus) {
        return orderRepository.findByOrderId(orderId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Order not found with ID: " + orderId)))
                .flatMap(existing -> {
                    existing.setOrderStatus(newStatus);
                    return orderRepository.save(existing);
                });
    }

    /**
     * Innovation Feature: Cancels an order and restores the reserved stock quantity
     * back to the corresponding product inventory.
     */
    public Mono<CustomerOrder> cancelOrderAndRestoreStock(Long orderId) {
        return orderRepository.findByOrderId(orderId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Order not found with ID: " + orderId)))
                .flatMap(order -> {
                    if ("Cancelled".equalsIgnoreCase(order.getOrderStatus())) {
                        return Mono.error(new IllegalArgumentException("Order " + orderId + " is already cancelled."));
                    }
                    return productRepository.findByProductId(order.getProductId())
                            .flatMap(product -> {
                                int restored = product.getStockQuantity() + order.getQuantity();
                                product.setStockQuantity(restored);
                                product.setAvailability(restored > 0);
                                order.setOrderStatus("Cancelled");
                                return productRepository.save(product).then(orderRepository.save(order));
                            });
                });
    }

    public Mono<Void> deleteOrder(Long orderId) {
        return orderRepository.findByOrderId(orderId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Order not found with ID: " + orderId)))
                .flatMap(existing -> orderRepository.deleteByOrderId(orderId));
    }
}
