#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdio.h>


// Must be intialized on module init
static uint32_t CRC_TABLE [256] = {0};

static void
InitCRCTable() {
    const uint32_t poly = 0xEDB88320U;
    for (uint32_t i = 0; i < 256U; ++i) {
        uint32_t crc = i;
        for (uint32_t j = 0; j < 8U; ++j) {
            if (crc & 0x1U) {
                crc = ((crc >> 1U) & 0x7FFFFFFFU) ^ poly;
            }
            else {
                crc = ((crc >> 1U) & 0x7FFFFFFFU);
            }
        }
        CRC_TABLE[i] = crc;
    }
}

static uint32_t
CRC32(uint8_t ch, uint32_t crc) {
    return ((crc >> 8U) & 0xFFFFFFU) ^ CRC_TABLE[(crc ^ ch) & 0xFFU];
}

typedef struct {
    PyObject_HEAD
    uint32_t key0;
    uint32_t key1;
    uint32_t key2;
} StandardZipDecrypterObject;

static void
UpdateKeys(StandardZipDecrypterObject *decrypter, uint8_t c) {
    decrypter->key0 = CRC32(c, decrypter->key0);
    decrypter->key1 = (decrypter->key1 + (decrypter->key0 & 0xFFU)) & 0xFFFFFFFFU;
    /* This formula is for a linear congruential generator to generate pseudo-random numbers. */
    decrypter->key1 = (decrypter->key1 * 134775813U + 1U) & 0xFFFFFFFFU;
    decrypter->key2 = CRC32((decrypter->key1 >> 24U) & 0xFFU, decrypter->key2);
}

static uint8_t
DecryptByte(StandardZipDecrypterObject *decrypter, uint8_t c) {
    const uint32_t k = decrypter->key2 | 2U;
    c = c ^ (((k * (k ^ 1U)) >> 8U) & 0xFF);
    UpdateKeys(decrypter, c);
    return c;
}

static PyObject *
DecryptBytes(StandardZipDecrypterObject *decrypter, PyObject *input) {
    const Py_ssize_t len = PyBytes_Size(input);
    // Return from here because malloc(0) is undefined
    if (len == 0) {
        return PyBytes_FromStringAndSize("", 0);
    }

    const uint8_t* const buffer = (const uint8_t*)PyBytes_AsString(input);

    uint8_t* output = malloc(len * sizeof(uint8_t));
    if (output == NULL) {
        return PyErr_NoMemory();
    }

    for (uint32_t i = 0; i < len; ++i) {
        output[i] = DecryptByte(decrypter, buffer[i]);
    }
    PyObject* const ret = PyBytes_FromStringAndSize((const char*)output, len);
    // Free allocated memory because it has been already copied to bytes object
    free(output);
    return ret;
}

static int
StandardZipDecrypter_init(StandardZipDecrypterObject *self, PyObject *args, PyObject *kwds) {
    const uint8_t *pwd = NULL;
    Py_ssize_t pwd_len = -1;

    if (!PyArg_ParseTuple(args, "y#", &pwd, &pwd_len)) {
        return -1;
    }

    self->key0 = 305419896;
    self->key1 = 591751049;
    self->key2 = 878082192;

    for (uint32_t i = 0; i < pwd_len; ++i) {
        UpdateKeys(self, pwd[i]);
    }
    return 0;
}

static PyObject *
StandardZipDecrypter_decrypt_bytes(StandardZipDecrypterObject *self, PyObject *args) {
    const PyObject* input;

    if (!PyArg_ParseTuple(args, "S", &input)) {
        return NULL;
    }

    return DecryptBytes(self, (PyObject*)input);
}

static PyObject *
StandardZipDecrypter_call(StandardZipDecrypterObject *self, PyObject *args, PyObject *kwds) {
    PyObject* input;

    if (!PyArg_ParseTuple(args, "O", &input)) {
        return NULL;
    }

    if (PyLong_CheckExact(input)) {
        const uint32_t c = PyLong_AsUnsignedLong(input);
        if (PyErr_Occurred()) {
            return NULL;
        }
        if (c > 255) {
            PyErr_SetString(PyExc_ValueError, "valid range of byte is [0-255]");
            return NULL;
        }
        return PyLong_FromLong(DecryptByte(self, (uint8_t) c));
    }

    if (PyBytes_CheckExact(input)) {
        return DecryptBytes(self, PyBytes_FromObject(input));
    }

    PyErr_SetString(PyExc_TypeError, "A bytes object or int is required.");

    return NULL;
}

static PyMethodDef StandardZipDecrypter_methods[] = {
    {
        .ml_name = "decrypt_bytes",
        .ml_meth = (PyCFunction) StandardZipDecrypter_decrypt_bytes,
        .ml_flags = METH_VARARGS,
        .ml_doc = "Decrypt and return bytes object"
    },
    {NULL}  /* Sentinel */
};


static PyType_Slot StandardZipDecrypter_slots[] = {
    {Py_tp_new, PyType_GenericNew},
    {Py_tp_init, (initproc) StandardZipDecrypter_init},
    {Py_tp_call, (ternaryfunc) StandardZipDecrypter_call},
    {Py_tp_methods, StandardZipDecrypter_methods},
    {0, NULL},  /* End-of-array token. */
};

static PyType_Spec StandardZipDecrypter_specification = {
    .name = "zipdecrypter.StandardZipDecrypter",
    .basicsize = sizeof(StandardZipDecrypterObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .slots = StandardZipDecrypter_slots,
};

static PyModuleDef zipdecrypterModule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_zipdecrypter",
    .m_size = -1
};


PyMODINIT_FUNC
PyInit__zipdecrypter() {
    PyObject* const standardZipDecrypterClass = PyType_FromSpec(&StandardZipDecrypter_specification);
    if (standardZipDecrypterClass == NULL) {
        return NULL;
    }

    PyObject * const m = PyModule_Create(&zipdecrypterModule);
    if (m == NULL) {
        return NULL;
    }

    if (PyModule_AddObject(m, "StandardZipDecrypter", standardZipDecrypterClass) != 0)
    {
        Py_DecRef(m);
        return NULL;
    }

    InitCRCTable();

    return m;
}
