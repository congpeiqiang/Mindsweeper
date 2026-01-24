#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/9 16:27
# @Author  : CongPeiQiang
# @File    : numpy_linalg.py
# @Software: PyCharm
import numpy as np

# 创建示例矩阵
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]], dtype=np.float64)

B = np.array([[2, 0, 1],
              [1, 2, 3],
              [4, 5, 6]], dtype=np.float64)

vec = np.array([1, 2, 3], dtype=np.float64)

# 计算特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eig(A)
print("特征值:", eigenvalues)
print("特征向量:\n", eigenvectors)

# 验证：A * v = λ * v
for i in range(len(eigenvalues)):
    v = eigenvectors[:, i]
    λ = eigenvalues[i]
    result = np.dot(A, v)
    expected = λ * v
    print(f"验证特征值{λ}:", np.allclose(result, expected))