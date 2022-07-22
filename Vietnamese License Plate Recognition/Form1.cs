using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Emgu.CV;
using Emgu.CV.Structure;
using Emgu.CV.UI;
using Emgu.CV.CvEnum;
using Emgu.CV.Util;
using Tesseract;
namespace Vietnamese_License_Plate_Recognition
{
    public partial class Form1 : Form
    {

        List<Image<Bgr, Byte>> PlateImagesList = new List<Image<Bgr, byte>>();
        public Form1()
        {
            InitializeComponent();
        }
        public TesseractEngine full_tesseract = new TesseractEngine(@"./data", "eng", EngineMode.Default);
        public TesseractEngine word_tesseract = new TesseractEngine(@"./data", "eng", EngineMode.Default);
        public TesseractEngine num_tesseract = new TesseractEngine(@"./data", "eng", EngineMode.Default);
       
        private void button1_Click(object sender, EventArgs e)
        {
            // open file dialog   
            OpenFileDialog open = new OpenFileDialog();
            // image filters  
            open.Filter = "Image Files(*.jpg; *.jpeg; *.gif; *.bmp)|*.jpg; *.jpeg; *.gif; *.bmp";
            if (open.ShowDialog() == DialogResult.OK)
            {
                // display image in picture box  
                string startupPath = open.FileName;
                Image<Rgb, Byte> img = new Image<Rgb, Byte>(startupPath);
                imageBox1.Image = img;
                Image<Gray, Byte> imgGray = new Image<Gray, Byte>(startupPath);
                //pictureBox1.Image = imgGray.ToBitmap();
                ProcessImage(startupPath);
            }
        }

        public void ProcessImage(string startupPath)
        {
            Bitmap image = new Bitmap(startupPath);
            FindLicensePlate(image, pictureBox1, imageBox1, PlateImagesList);
        }
        //Hàm xử lý biển số xe 
        public void FindLicensePlate(Bitmap image, PictureBox pictureBox1, ImageBox imageBox1, List<Image<Bgr, byte>> plateImagesList)
        {
            try
            {
                //Detect biển số xe
                Image<Bgr, byte> image2 = new Image<Bgr, byte>(image);
                CascadeClassifier classifier = new CascadeClassifier(Application.StartupPath + "\\output-hv-33-x25.xml");
                var imgGray = image2.Convert<Gray, byte>().Clone();
                Rectangle[] plates = classifier.DetectMultiScale(imgGray, 1.1, 4);
                if (plates.Length == 0)
                {
                    MessageBox.Show("Không thể nhận dạng được biển số xe này !", "TD SJC");
                    return;
                }

                foreach (Rectangle plate in plates)
                {
                    if (plate.Width > 20 && plate.Width < 250 && plate.Height >10 && plate.Height < 250)
                    {
                        image2.Draw(plate, new Bgr(0, 255, 0), 2);
                        imageBox1.Image = image2;
                        Image<Bgr, byte> image3 = new Image<Bgr, byte>(image);
                        image3.ROI = plate;
                        pictureBox1.Image = image3.Resize(500, 500, Inter.Cubic, preserveScale: true).Bitmap;
                        //Console.WriteLine("W: {0}, H: {1}", plate.Width, plate.Height);
                    }      
                    else
                    {
                        MessageBox.Show("Không nhận diện được. Thử lại ảnh khác !", "TD SJC");
                        return;
                    }    
                }
                //Tìm Contours cho biển số vừa detect được
                Image<Bgr, byte> src = new Image<Bgr, byte>(new Bitmap(pictureBox1.Image));
                IdentifyContours(src);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
        public static string OCR(Bitmap image, bool isFull, TesseractEngine full_tesseract, TesseractEngine num_tesseract, TesseractEngine word_tesseract, bool isNum = false)
        {
            full_tesseract.SetVariable("tessedit_char_whitelist", "ABCDEFGHKLMNPQRSTUVWXYZ123456789");
            word_tesseract.SetVariable("tessedit_char_whitelist", "ABCDEFGHKLMNPQRSTUVWXYZ");
            num_tesseract.SetVariable("tessedit_char_whitelist", "0123456789");
            TesseractEngine tesseractProcessor = isFull ? full_tesseract : ((isNum) ? num_tesseract : word_tesseract);
            var page = tesseractProcessor.Process(image, PageSegMode.SingleChar);
            string text =  page.GetText();
            page.Dispose();
            return text;
        }
        public void IdentifyContours(Image<Bgr,byte> colorImage)
        {
            List<Rectangle> listRect = new List<Rectangle>();
            Image<Gray, byte> srcGray = colorImage.Convert<Gray, byte>();
            Image<Gray, byte> imageT = new Image<Gray, byte>(srcGray.Width, srcGray.Height);
            CvInvoke.AdaptiveThreshold(srcGray, imageT, 255.0, AdaptiveThresholdType.MeanC, ThresholdType.Binary, 101, 5.0);           
            Image<Gray, byte> imageThresh = imageT;
            pictureBox3.Image = imageT.Bitmap;
            imageT = imageT.ThresholdBinary(new Gray(100), new Gray(255.0));//Cần xử lý thêm để nhận dạng tốt hơn
            VectorOfVectorOfPoint contour = new VectorOfVectorOfPoint();
            Mat hier = new Mat();
            CvInvoke.FindContours(imageT, contour, hier, RetrType.List, ChainApproxMethod.ChainApproxSimple);
            if (contour.Size > 0)
            {     
                for (int c = 0; c < contour.Size; c++)
                {         
                    Rectangle rect = CvInvoke.BoundingRectangle(contour[c]);                   
                    //double area = CvInvoke.ContourArea(contour[c]);
                    //double rate = (double)rect.Width / (double)rect.Height;
                    if (rect.Width > 30 && rect.Width <150 && rect.Height > 100 && rect.Height < 200 && rect.X > 10 && rect.Y >10)
                    {
                        //Console.WriteLine("X: {0}, Y: {1}, W: {2}, H: {3}", rect.X, rect.Y,rect.Width,rect.Height);
                        CvInvoke.Rectangle(colorImage, rect, new MCvScalar(0, 0, 255),1);
                        listRect.Add(rect);                      
                    }                                   
                }
            }
            //Lọc và sắp xếp các Rectangle
            ///Xác định dòng 1, dòng 2 của biển
            List<Rectangle> up = new List<Rectangle>();
            List<Rectangle> dow = new List<Rectangle>();
            int up_y = 0, dow_y = 0;
            bool flag_up = false;
            if (listRect == null) return;
            for (int i = 0; i < listRect.Count; i++)
            {
                for (int j = i; j < listRect.Count; j++)
                {
                    if (listRect[i].Y > listRect[j].Y + 100)
                    {
                        flag_up = true;
                        up_y = listRect[j].Y;
                        dow_y = listRect[i].Y;
                        break;
                    }
                    else if (listRect[j].Y > listRect[i].Y + 100)
                    {
                        flag_up = true;
                        up_y = listRect[i].Y;
                        dow_y = listRect[j].Y;
                        break;
                    }
                    if (flag_up == true) break;
                }
            }
            for (int i = 0; i < listRect.Count; i++)
            {
                //Up Plate
                if (listRect[i].Y < up_y + 50 && listRect[i].Y > up_y - 50)
                {
                    up.Add(listRect[i]);
                }
                //Dow Plate
                else if (listRect[i].Y < dow_y + 50 && listRect[i].Y > dow_y - 50)
                {
                    dow.Add(listRect[i]);
                }
            }
            if (flag_up == false) dow = listRect;
            //Sắp xếp các số trong Up PLate
            for (int i = 0; i < up.Count; i++)
            {
                for (int j = i; j < up.Count; j++)
                {
                    if (up[i].X > up[j].X)
                    {
                        Rectangle w = up[i];
                        up[i] = up[j];
                        up[j] = w;
                    }
                }
            }
            //Sắp xếp các số trong Dow PLate
            for (int i = 0; i < dow.Count; i++)
            {
                for (int j = i; j < dow.Count; j++)
                {
                    if (dow[i].X > dow[j].X)
                    {
                        Rectangle w = dow[i];
                        dow[i] = dow[j];
                        dow[j] = w;
                    }
                }
            }
            string textPlates = "";
            for (int i = 0; i < up.Count; i++)
            {
                Image<Gray, byte> imageCrop = new Image<Gray, byte>(imageThresh.Bitmap);
                imageCrop.ROI = up[i];               
                imageCrop = imageCrop.Dilate(2);
                imageCrop = imageCrop.Erode(2);
                Image<Bgr, Byte> imgResize = new Image<Bgr, Byte>(imageCrop.Width * 2, imageCrop.Height * 2, new Bgr(255, 255, 255));
                using (Graphics g = Graphics.FromImage(imgResize.Bitmap))
                {
                    g.DrawImage(imageCrop.Bitmap, imageCrop.Width / 2, imageCrop.Height / 2);
                }
                string temp;
                if (i < 2)
                {
                    //CvInvoke.Imshow("Numbers Plates(i<2)", imgResize);
                    //CvInvoke.WaitKey(0);
                    temp = OCR(imgResize.Bitmap, false, full_tesseract, num_tesseract, word_tesseract, true);
                    //Console.WriteLine(temp);
                }
                else if (i == 2)
                {
                    //CvInvoke.Imshow("Numbers Plates(i==3)", imgResize);
                    //CvInvoke.WaitKey(0);
                    temp = OCR(imgResize.Bitmap, false, full_tesseract, num_tesseract, word_tesseract, false);
                    //Console.WriteLine(temp);
                }
                else
                {
                    //CvInvoke.Imshow("Numbers Plates(i>3)", imgResize);
                    //CvInvoke.WaitKey(0);
                    temp = OCR(imgResize.Bitmap, true, full_tesseract, num_tesseract, word_tesseract, false);
                    //Console.WriteLine(temp);
                }
                textPlates += temp;
                //Image<Gray, byte> resizedImage = imageCrop.Resize(50, 90, Inter.Linear);
                //Image<Bgr, Byte> imgResize = new Image<Bgr, Byte>(imageCrop.Width * 5, imageCrop.Height * 2, new Bgr(255, 255, 255));
                //using (Graphics g = Graphics.FromImage(imgResize.Bitmap))
                //{
                //    g.DrawImage(imageCrop.Resize(20, 20, Inter.Cubic, preserveScale: true).Bitmap, imageCrop.Width * 2, imageCrop.Height / 2); ;
                //}
                //Image<Gray, byte> imageTest = new Image<Gray, byte>(imgResize.Width, imgResize.Height);
                //CvInvoke.AdaptiveThreshold(imgResize.Convert<Gray, byte>(), imageTest, 255.0, AdaptiveThresholdType.MeanC, ThresholdType.BinaryInv, 21, 2);
                //Console.WriteLine(t);
                //Mat imgCropResize = imgResize.Mat;
                //CvInvoke.Imshow("Numbers Plates", imageCrop);
                //Console.WriteLine("W: {0}, H: {1}", imgResize.Width, imgResize.Height);
                //CvInvoke.WaitKey(0);
            }
            textPlates += "\r\n";
            for (int i = 0; i < dow.Count; i++)
            {
                Image<Gray, byte> imageCrop = new Image<Gray, byte>(imageThresh.Bitmap);
                imageCrop.ROI = dow[i];
                imageCrop = imageCrop.Dilate(2);
                imageCrop = imageCrop.Erode(2);
                //imageCrop = imageCrop.Dilate(1);
                Image<Bgr, Byte> imgResize = new Image<Bgr, Byte>(imageCrop.Width * 2, imageCrop.Height * 2, new Bgr(255, 255, 255));
                using (Graphics g = Graphics.FromImage(imgResize.Bitmap))
                {
                    g.DrawImage(imageCrop.Bitmap, imageCrop.Width / 2, imageCrop.Height / 2);
                }
                //CvInvoke.Imshow("Numbers Plates(imgD)", imgResize);
                //CvInvoke.WaitKey(0);
                string temp = OCR(imgResize.Bitmap, false, full_tesseract, num_tesseract, word_tesseract, true);
                //Console.WriteLine(temp);
                textPlates += temp;
            }
            //Crop ảnh và hiển thị ra pictureBox
            var cropUp = cutPlates(up,out double chenhlech);
            var cropDow = cutPlates(dow, out double chechlech);
            double w_bounding = Convert.ToDouble(cropDow.Width);
            double angle = Math.Atan(Convert.ToDouble(chechlech / (w_bounding))) * (180 / Math.PI);
            Image<Gray, byte> imageCropUp = imageThresh.Dilate(1);
            imageCropUp.ROI = cropUp;
            var imgcropU = rotateImage(imageCropUp.Bitmap,-angle);
            Image<Bgr, Byte> imgU= new Image<Bgr, Byte>(imgcropU.Width * 2, imgcropU.Height * 2, new Bgr(255, 255, 255));
            using (Graphics g = Graphics.FromImage(imgU.Bitmap))
            {
                g.DrawImage(imgcropU, imgcropU.Width / 2, imgcropU.Height / 2);
            }
            Image<Gray, byte> imageCropDow= imageThresh.Dilate(1);
            imageCropDow.ROI = cropDow;
            var imgCropD = rotateImage(imageCropDow.Bitmap,-angle);
            Image<Bgr, Byte> imgD = new Image<Bgr, Byte>(imgCropD.Width*2, imgCropD.Height * 2, new Bgr(255, 255, 255));
            using (Graphics g = Graphics.FromImage(imgD.Bitmap))
            {
                g.DrawImage(imgCropD, imgCropD.Width / 2, imgCropD.Height / 2);
            }
            //CvInvoke.Imwrite("line1.jpg", imgU);
            //CvInvoke.Imwrite("line2.jpg", imgD);
            //var Result1 = new IronTesseract().Read(@"line1.jpg");
            //var Result2 = new IronTesseract().Read(@"line2.jpg");
            //Console.WriteLine(Result1.Text+ "\r\n" + Result2.Text);
            pictureBox4.Image = imgU.Bitmap;
            pictureBox5.Image = imgD.Bitmap;
            pictureBox2.Image = colorImage.Bitmap;
            //string NumberPlate = OCR(imgU.Bitmap,true,full_tesseract,num_tesseract, word_tesseract, false) + "\r\n" + OCR(imgD.Bitmap, false, full_tesseract, num_tesseract, word_tesseract, true);
            textBox1.Text = textPlates;
        }
        public static Bitmap rotateImage(Bitmap b, double angle)
        {
            //create a new empty bitmap to hold rotated image
            Bitmap returnBitmap = new Bitmap(b.Width, b.Height);
            //make a graphics object from the empty bitmap
            Graphics g = Graphics.FromImage(returnBitmap);
            g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
            //move rotation point to center of image
            g.TranslateTransform((float)b.Width / 2, (float)b.Height / 2);
            //rotate
            g.RotateTransform(Convert.ToSingle(angle));
            //move image back
            g.TranslateTransform(-(float)b.Width / 2, -(float)b.Height / 2);
            //draw passed in image onto graphics object
            g.DrawImage(b, new Point(0, 0));
            return returnBitmap;
        }
        public Rectangle cutPlates(List<Rectangle> listRect, out double chenhlech)
        {
            Rectangle Bien = new Rectangle();
            int xmin = listRect[0].X, xmax = listRect[0].X + listRect[0].Width;
            int ymin = listRect[0].Y, ymax = listRect[0].Y;
            int Y = 0;
            int Height = 0;
            for (int i = 0; i < listRect.Count; i++)
            {
                if (xmin > listRect[i].X)
                {
                    xmin = listRect[i].X;
                    ymin = listRect[i].Y;
                }
                if (xmax < listRect[i].X + listRect[i].Width)
                {
                    xmax = listRect[i].X + listRect[i].Width;
                    ymax = listRect[i].Y;
                }
                Y += listRect[i].Y;
                Height += listRect[i].Height;
            }
            Bien.X = xmin-10;
            Bien.Y = Y / listRect.Count-10;
            Bien.Width = xmax - xmin +20;
            Bien.Height = Height / listRect.Count +20;
            chenhlech = ymax - ymin;
            return Bien;
        }
    }
}
