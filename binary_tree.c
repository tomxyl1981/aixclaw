#include <stdio.h>
#include <stdlib.h>

// 二叉树节点结构
typedef struct TreeNode {
    int data;
    struct TreeNode *left;
    struct TreeNode *right;
} TreeNode;

// 创建新节点
TreeNode* createNode(int data) {
    TreeNode* newNode = (TreeNode*)malloc(sizeof(TreeNode));
    if (newNode == NULL) {
        printf("内存分配失败\n");
        return NULL;
    }
    newNode->data = data;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

// 插入节点（二叉搜索树）
TreeNode* insert(TreeNode* root, int data) {
    if (root == NULL) {
        return createNode(data);
    }
    
    if (data < root->data) {
        root->left = insert(root->left, data);
    } else if (data > root->data) {
        root->right = insert(root->right, data);
    }
    
    return root;
}

// 前序遍历（根-左-右）
void preOrder(TreeNode* root) {
    if (root != NULL) {
        printf("%d ", root->data);
        preOrder(root->left);
        preOrder(root->right);
    }
}

// 中序遍历（左-根-右）
void inOrder(TreeNode* root) {
    if (root != NULL) {
        inOrder(root->left);
        printf("%d ", root->data);
        inOrder(root->right);
    }
}

// 后序遍历（左-右-根）
void postOrder(TreeNode* root) {
    if (root != NULL) {
        postOrder(root->left);
        postOrder(root->right);
        printf("%d ", root->data);
    }
}

// 查找节点
TreeNode* search(TreeNode* root, int data) {
    if (root == NULL || root->data == data) {
        return root;
    }
    
    if (data < root->data) {
        return search(root->left, data);
    }
    
    return search(root->right, data);
}

// 查找最小值节点
TreeNode* findMin(TreeNode* root) {
    while (root->left != NULL) {
        root = root->left;
    }
    return root;
}

// 删除节点
TreeNode* deleteNode(TreeNode* root, int data) {
    if (root == NULL) {
        return root;
    }
    
    if (data < root->data) {
        root->left = deleteNode(root->left, data);
    } else if (data > root->data) {
        root->right = deleteNode(root->right, data);
    } else {
        // 找到要删除的节点
        
        // 情况1：叶子节点或只有一个子节点
        if (root->left == NULL) {
            TreeNode* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            TreeNode* temp = root->left;
            free(root);
            return temp;
        }
        
        // 情况2：有两个子节点
        TreeNode* temp = findMin(root->right);
        root->data = temp->data;
        root->right = deleteNode(root->right, temp->data);
    }
    
    return root;
}

// 计算树的高度
int height(TreeNode* root) {
    if (root == NULL) {
        return 0;
    }
    
    int leftHeight = height(root->left);
    int rightHeight = height(root->right);
    
    return (leftHeight > rightHeight ? leftHeight : rightHeight) + 1;
}

// 释放整棵树
void freeTree(TreeNode* root) {
    if (root != NULL) {
        freeTree(root->left);
        freeTree(root->right);
        free(root);
    }
}

// 主函数测试
int main() {
    TreeNode* root = NULL;
    
    // 插入节点
    root = insert(root, 50);
    insert(root, 30);
    insert(root, 20);
    insert(root, 40);
    insert(root, 70);
    insert(root, 60);
    insert(root, 80);
    
    printf("前序遍历: ");
    preOrder(root);
    printf("\n");
    
    printf("中序遍历: ");
    inOrder(root);
    printf("\n");
    
    printf("后序遍历: ");
    postOrder(root);
    printf("\n");
    
    printf("树的高度: %d\n", height(root));
    
    // 查找测试
    int searchValue = 40;
    TreeNode* result = search(root, searchValue);
    if (result != NULL) {
        printf("找到节点: %d\n", searchValue);
    } else {
        printf("未找到节点: %d\n", searchValue);
    }
    
    // 删除测试
    printf("\n删除节点 20\n");
    root = deleteNode(root, 20);
    printf("中序遍历: ");
    inOrder(root);
    printf("\n");
    
    // 释放内存
    freeTree(root);
    
    return 0;
}
