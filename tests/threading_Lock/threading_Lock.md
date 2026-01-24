在Python中，threading.Lock() 是一个用于同步线程的原始锁。它有两个基本方法：acquire() 和 release()。
当一个线程通过调用acquire()方法获得锁时，其他线程再调用acquire()时会被阻塞，直到锁被释放。
锁可以用release()方法释放。 使用锁可以确保在同一时刻只有一个线程可以访问共享资源，从而避免竞态条件。

Python 中的 threading.Lock() 是一个同步原语，用于多线程编程中保护共享资源，防止多个线程同时访问导致数据不一致。
