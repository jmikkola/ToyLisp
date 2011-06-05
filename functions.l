(defun zip (a b)
   (if a 
        (if b
            (cat
                (list 
                    (first a)
                    (first b))
                (zip 
                    (rest a)
                    (rest b)))
            ())
        ())) 

(defun map (f l) (if l
    (cat (f (first l))
        (map f (rest l)))
    ()))

(defun length (l) (if l
    (+ 1 (length (rest l)))
    0))

(defun sum (l) (if l
    (+ (first l) (sum (rest l)))
    0))

(defun max2 (a b)
    (if (> a b) a b))

(defun max (l) 
    (if l
        (max2 
            (first l)
            (max (rest l)))
        (+ 0 0)))

(defun snd (x) (first (rest x)))
